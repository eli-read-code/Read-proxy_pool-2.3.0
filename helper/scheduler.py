# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: __runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
-------------------------------------------------
"""
__author__ = 'JHao'
"""
eli::
APScheduler 基于Quartz的一个Python定时任务框架，实现了Quartz的所有功能，使用起来十分方便。
提供了基于日期、固定时间间隔以及crontab类型的任务，并且可以持久化任务。基于这些功能，我们可以很方便的实现一个python定时任务系统。
add_job的第二个参数是trigger，它管理着作业的调度方式。它可以为date, interval或者cron。对于不同的trigger，对应的参数也相同。
(1). cron定时调度（某一定时时刻执行）
(2). interval 间隔调度（每隔多久执行）
(3). date 定时调度（作业只会执行一次,某个时间点）

"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler



def __runProxyFetch():
    proxy_queue = Queue()  # eli::from queue import Queue,python内置STL[标准模板库（Standard Template Library，STL）]
    proxy_fetcher = Fetcher()

    for proxy in proxy_fetcher.run():  # eli::fetch proxy with proxyFetcher
        proxy_queue.put(proxy)

    Checker("raw", proxy_queue)


def __runProxyCheck():
    proxy_queue = Queue()
    proxy_handler = ProxyHandler()
    if proxy_handler.db.getCount().get("total", 0) < proxy_handler.conf.poolSizeMin:
        # eli::数据库proxy记录数小于配置的最小值,调用__runProxyFetch()抓取数据
        __runProxyFetch()
    else:
        for proxy in proxy_handler.getAll():  # eli::从数据库读取返回数据
            proxy_queue.put(proxy)
        Checker("use", proxy_queue)


# eli::第三方调用函数
def runScheduler():
    __runProxyFetch()

    timezone = ConfigHandler().timezone  # eli::设置时区
    scheduler_log = LogHandler("scheduler")
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)  # 定时任务调度器

    scheduler.add_job(__runProxyFetch, 'interval', minutes=4, id="proxy_fetch", name="proxy采集")  # 间隔4分钟调度一次
    scheduler.add_job(__runProxyCheck, 'interval', minutes=2, id="proxy_check", name="proxy检查")  # 间隔2分钟调度一次
    executors = {
        """设置线程池和进程池的最大数目"""
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }
    """
    查看下面的configure,源码如下:
    job_defaults = config.get('job_defaults', {})
        self._job_defaults = {
            'misfire_grace_time': asint(job_defaults.get('misfire_grace_time', 1)),
            'coalesce': asbool(job_defaults.get('coalesce', True)),
            'max_instances': asint(job_defaults.get('max_instances', 1))
        }
    misfire_grace_time：超过用户设定的时间范围外，该任务依旧执行的时间(单位时间s)。
    比如用户设置misfire_grace_time=60,于3:00触发任务。
    由于某种原因在3:00没有触发，被延时了。如果时间在3:01内，该任务仍能触发，超过3:01任务不执行。
    
    coalesce：累计的 任务是否执行。True不执行，False,执行。
    同上，由于某种原因，比如进场挂了，导致任务多次没有调用，则前几次的累计任务的任务是否执行的策略。
    
    max_instances：同一个任务在线程池中最多跑的实例数。
    """
    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)

    scheduler.start()
