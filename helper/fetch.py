# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fetchScheduler
   Description :
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06:
-------------------------------------------------
"""
__author__ = 'JHao'

from helper.proxy import Proxy
from helper.check import DoValidator
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from fetcher.proxyFetcher import ProxyFetcher
from handler.configHandler import ConfigHandler


class Fetcher(object):
    name = "fetcher"

    def __init__(self):
        self.log = LogHandler(self.name)
        self.conf = ConfigHandler()
        self.proxy_handler = ProxyHandler()

    def run(self):
        """
        fetch proxy with proxyFetcher
        :return:
        """
        proxy_dict = dict()
        self.log.info("ProxyFetch : start")
        for fetch_source in self.conf.fetchers:
            self.log.info("ProxyFetch - {func}: start".format(
                func=fetch_source))  # eli::fetch_source=freeProxy01,freeProxy02,,,配置文件中的:PROXY_FETCHER
            fetcher = getattr(ProxyFetcher, fetch_source,
                              None)  # eli::从 ProxyFetcher 对象中找出fetch_source对应的函数:freeProxy01()

            """eli:: 下面是fetcher的异常处理"""
            if not fetcher:
                self.log.error("ProxyFetch - {func}: class method not exists!".format(func=fetch_source))
                continue
            if not callable(fetcher):
                self.log.error("ProxyFetch - {func}: must be class method".format(func=fetch_source))
                continue

            """eli:: 各个fetcher()函数: yield '%s:%s' % (ip, port)"""
            try:
                for proxy in fetcher():
                    self.log.info('ProxyFetch - %s: %s ok' % (
                    fetch_source, proxy.ljust(23))) # eli::Python ljust() 方法返回一个原字符串左对齐,并使用空格填充至指定长度的新字符串。如果指定的长度小于原字符串的长度则返回原字符串。
                    # eli::[print]ProxyFetch - freeProxy02: 45.184.155.4:999        ok
                    proxy = proxy.strip()
                    if proxy in proxy_dict:
                        proxy_dict[proxy].add_source(fetch_source) # eli::如果存在proxy对象,给其增加源
                    else:
                        proxy_dict[proxy] = Proxy(proxy, source=fetch_source) # eli::如果不存在proxy-key,增加proxy对象
            except Exception as e:
                self.log.error("ProxyFetch - {func}: error".format(func=fetch_source))
                self.log.error(str(e))
        self.log.info("ProxyFetch - all complete!")
        for _ in proxy_dict.values():
            if DoValidator.preValidator(_.proxy):
                yield _
