# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxy_pool
   Description :   proxy pool 启动入口
   Author :        JHao
   date：          2020/6/19
-------------------------------------------------
   Change Activity:
                   2020/6/19:
-------------------------------------------------
"""
"""
# eli::
# Click 是 Flask 的团队 pallets 开发的优秀开源项目，它为命令行工具的开发封装了大量方法，使开发者只需要专注于功能实现。
# 详细见文档:https://click.palletsprojects.com/en/8.0.x/
"""

__author__ = 'clever-eli'

import click # eli::命令行工具
from helper.launcher import startServer, startScheduler
from setting import BANNER, VERSION # eli::图标:[Proxypool], 版本号:"2.3.0"

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help','--he'])
# eli::{'help_option_names':['-h', '--help']}

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=VERSION) # eli::设置版本
def cli():
    """ProxyPool cli工具"""


@cli.command(name="schedule-eli")
def schedule():
    """ 启动调度程序 """
    click.echo(BANNER) # eli::命令行显示图标:[Proxypool]
    startScheduler()


@cli.command(name="server-eli")
def server():
    """ 启动api服务 """
    click.echo(BANNER) # eli::命令行显示图标:[Proxypool]
    startServer()


if __name__ == '__main__':
    cli()
