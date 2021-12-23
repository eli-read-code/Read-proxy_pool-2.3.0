# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     launcher
   Description :   启动器
   Author :        JHao
   date：          2021/3/26
-------------------------------------------------
   Change Activity:
                   2021/3/26: 启动器
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from db.dbClient import DbClient
from handler.logHandler import LogHandler
from handler.configHandler import ConfigHandler

log = LogHandler('launcher')


def startServer():
    __beforeStart()
    from api.proxyApi import runFlask
    runFlask()


def startScheduler():
    __beforeStart() # eli::启动爬虫调度器前的准备工作
    from helper.scheduler import runScheduler
    runScheduler() # eli::启动爬虫调度器


def __beforeStart():
    __showVersion() # eli::显示版本号
    __showConfigure() # eli::显示serverHost,serverPort,dbConn,fetchers
    if __checkDBConfig(): # eli:: 创建数据库连接client,仅存在数据库连接异常时返回异常信息
        log.info('exit!')
        sys.exit()


def __showVersion():
    from setting import VERSION
    log.info("ProxyPool Version: %s" % VERSION)


def __showConfigure():
    conf = ConfigHandler()
    log.info("ProxyPool configure HOST: %s" % conf.serverHost)
    log.info("ProxyPool configure PORT: %s" % conf.serverPort)
    log.info("ProxyPool configure DB_CONN: %s" % conf.dbConn)
    log.info("ProxyPool configure PROXY_FETCHER: %s" % conf.fetchers)


def __checkDBConfig():
    """
    eli::db.test()返回的是: except XXXException as e,---返回的是异常信息
    """
    conf = ConfigHandler() # ConfigHandler,懒加载返回配置信息
    db = DbClient(conf.dbConn) # DbClient DB工厂类,创建数据库连接客户端client
    log.info("============ DATABASE CONFIGURE ================")
    log.info("DB_TYPE: %s" % db.db_type)
    log.info("DB_HOST: %s" % db.db_host)
    log.info("DB_PORT: %s" % db.db_port)
    log.info("DB_NAME: %s" % db.db_name)
    log.info("DB_USER: %s" % db.db_user)
    log.info("=================================================")
    return db.test()

