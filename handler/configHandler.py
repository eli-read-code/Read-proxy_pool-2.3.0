# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     configHandler
   Description :
   Author :        JHao
   date：          2020/6/22
-------------------------------------------------
   Change Activity:
                   2020/6/22:
                   ConfigHandler----懒加载返回配置信息
-------------------------------------------------
"""
"""
eli::读取返回配置信息
os.environ.get（）是python中os模块获取环境变量的一个方法
os.environ.get("HOST", setting.HOST) # 获取环境变量,不存在则返回setting.HOST

"""
__author__ = 'JHao'

import os
import setting
from util.singleton import Singleton
from util.lazyProperty import LazyProperty
from util.six import reload_six, withMetaclass


class ConfigHandler(withMetaclass(Singleton)):

    def __init__(self):
        pass

    @LazyProperty
    def serverHost(self):
        return os.environ.get("HOST", setting.HOST) # 获取环境变量,不存在则返回setting.HOST

    @LazyProperty
    def serverPort(self):
        return os.environ.get("PORT", setting.PORT)

    @LazyProperty
    def dbConn(self):
        return os.getenv("DB_CONN", setting.DB_CONN)

    @LazyProperty
    def tableName(self):
        return os.getenv("TABLE_NAME", setting.TABLE_NAME)

    @property
    def fetchers(self):
        reload_six(setting) # eli::重新加载配置文件
        return setting.PROXY_FETCHER

    @LazyProperty
    def httpUrl(self):
        return os.getenv("HTTP_URL", setting.HTTP_URL)

    @LazyProperty
    def httpsUrl(self):
        return os.getenv("HTTPS_URL", setting.HTTPS_URL)

    @LazyProperty
    def verifyTimeout(self):
        return os.getenv("VERIFY_TIMEOUT", setting.VERIFY_TIMEOUT)

    # @LazyProperty
    # def proxyCheckCount(self):
    #     return os.getenv("PROXY_CHECK_COUNT", setting.PROXY_CHECK_COUNT)

    @LazyProperty
    def maxFailCount(self):
        return os.getenv("MAX_FAIL_COUNT", setting.MAX_FAIL_COUNT)

    # @LazyProperty
    # def maxFailRate(self):
    #     return os.getenv("MAX_FAIL_RATE", setting.MAX_FAIL_RATE)

    @LazyProperty
    def poolSizeMin(self):
        return os.getenv("POOL_SIZE_MIN", setting.POOL_SIZE_MIN)

    @LazyProperty
    def timezone(self):
        return os.getenv("TIMEZONE", setting.TIMEZONE)

