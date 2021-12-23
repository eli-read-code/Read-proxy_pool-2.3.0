# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ssdbClient.py
   Description :   封装SSDB操作
   Author :        JHao
   date：          2016/12/2
-------------------------------------------------
   Change Activity:
                   2016/12/2:
                   2017/09/22: PY3中 redis-py返回的数据是bytes型
                   2017/09/27: 修改pop()方法 返回{proxy:value}字典
                   2020/07/03: 2.1.0 优化代码结构
                   2021/05/26: 区分http和https代理
-------------------------------------------------
"""
__author__ = 'JHao'
from redis.exceptions import TimeoutError, ConnectionError, ResponseError
from redis.connection import BlockingConnectionPool
from handler.logHandler import LogHandler
from random import choice
from redis import Redis
import json
"""
[SSDB]
一个高性能的支持丰富数据结构的 NoSQL 数据库, 用于替代 Redis.
特性
替代 Redis 数据库, Redis 的 100 倍容量
LevelDB 网络支持, 使用 C/C++ 开发
Redis API 兼容, 支持 Redis 客户端
适合存储集合数据, 如 list, hash, zset...
客户端 API 支持的语言包括: C++, PHP, Python, Java, Go
持久化的队列服务
主从复制, 负载均衡

[redis OR SSDB]
redis是内存数据库，ssdb是面向硬盘的存储，二者在存储格式和读写方式上有着根本的不同。
前面回答里提到的zrevrange 和 zrevrangebyscore慢，而zrange 和 zrangebyscore 还能接受，
其实就是说逆序遍历比顺序遍历慢得多，其根本原因就在于逆序遍历的时候，会多一个“记录头部”定位的过程，
需要不断尝试去定位到两条记录的“分界点”，而顺序遍历的时候则不需要，因为读完一条记录直接就到了下一条记录的“分界点”，
并且像rocksdb之类的存储引擎都会把数据长度保存在记录的元信息里，只需要按长度读取数据就可以了。
redis则不存在类似问题，因为它是完全基于指针和偏移量在内存中进行寻址来读取数据的，寻址效率高了好多个数量级。
ssdb貌似就是一个个人项目，但代码质量还是不错的，整个设计思想比较简洁。ssdb的主从复制效率很低。
binlog和数据是分开存储的，日志冗余较多，由于ssdb本身要在多线程条件下才能发挥出更好的性能，
为了使多个线程在写入binlog时能保证操作顺序和原子性，ssdb的binlog数据结构上用了一把全局锁，
可想而知，这里的锁竞争会很影响性能。另外，ssdb默认也没有集群管理的支持。
ssdb的好处，和swapdb(http://github.com/JRHZRD/swapdb)一样，都可以省钱。
如果有需要，可以尝试swapdb，它结合了redis和ssdb的优点，实现了基于LFU的热度统计和冷热交换，
做到了低成本和高性能的高平衡。
redis的好处，那就多了。缺点就是纯内存，比用SSD花钱。
"""

class SsdbClient(object):
    """
    SSDB client

    SSDB中代理存放的结构为hash：
    key为代理的ip:por, value为代理属性的字典;
    """

    def __init__(self, **kwargs):
        """
        init
        :param host: host
        :param port: port
        :param password: password
        :return:
        """
        self.name = ""
        kwargs.pop("username")
        self.__conn = Redis(connection_pool=BlockingConnectionPool(decode_responses=True,
                                                                   timeout=5,
                                                                   socket_timeout=5,
                                                                   **kwargs))

    def get(self, https):
        """
        从hash中随机返回一个代理
        :return:
        """
        if https:
            items_dict = self.__conn.hgetall(self.name)
            proxies = list(filter(lambda x: json.loads(x).get("https"), items_dict.values()))
            return choice(proxies) if proxies else None
        else:
            proxies = self.__conn.hkeys(self.name)
            proxy = choice(proxies) if proxies else None
            return self.__conn.hget(self.name, proxy) if proxy else None

    def put(self, proxy_obj):
        """
        将代理放入hash
        :param proxy_obj: Proxy obj
        :return:
        """
        result = self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)
        return result

    def pop(self, https):
        """
        顺序弹出一个代理
        :return: proxy
        """
        proxy = self.get(https)
        if proxy:
            self.__conn.hdel(self.name, json.loads(proxy).get("proxy", ""))
        return proxy if proxy else None

    def delete(self, proxy_str):
        """
        移除指定代理, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        self.__conn.hdel(self.name, proxy_str)

    def exists(self, proxy_str):
        """
        判断指定代理是否存在, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        return self.__conn.hexists(self.name, proxy_str)

    def update(self, proxy_obj):
        """
        更新 proxy 属性
        :param proxy_obj:
        :return:
        """
        self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)

    def getAll(self, https):
        """
        字典形式返回所有代理, 使用changeTable指定hash name
        :return:
        """
        item_dict = self.__conn.hgetall(self.name)
        if https:
            return list(filter(lambda x: json.loads(x).get("https"), item_dict.values()))
        else:
            return item_dict.values()

    def clear(self):
        """
        清空所有代理, 使用changeTable指定hash name
        :return:
        """
        return self.__conn.delete(self.name)

    def getCount(self):
        """
        返回代理数量
        :return:
        """
        proxies = self.getAll(https=False)
        return {'total': len(proxies), 'https': len(list(filter(lambda x: json.loads(x).get("https"), proxies)))}

    def changeTable(self, name):
        """
        切换操作对象
        :param name:
        :return:
        """
        self.name = name

    def test(self):
        log = LogHandler('ssdb_client')
        try:
            self.getCount()
        except TimeoutError as e:
            log.error('ssdb connection time out: %s' % str(e), exc_info=True)
            return e
        except ConnectionError as e:
            log.error('ssdb connection error: %s' % str(e), exc_info=True)
            return e
        except ResponseError as e:
            log.error('ssdb connection error: %s' % str(e), exc_info=True)
            return e
