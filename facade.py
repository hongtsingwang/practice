#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2016/12/17 14:42
# @Author   : Wang Hongqing
# @File     : Server.py
# @Software : PyCharm

import os
import sys
import logging
import argparse
import datetime
from abc import ABCMeta, abstractmethod
from enum import Enum

reload(sys)
sys.setdefaultencoding("utf-8")

State = Enum('State', 'new running sleeping restart zombie')


class Server():
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    def __str__(self):
        return self.name

    @abstractmethod
    def boot(self):
        pass

    @abstractmethod
    def kill(self, restart=True):
        pass


class FileServer(Server):
    def __init__(self):
        """初始化文件服务进程要求的操作"""
        self.name = 'FileServer'
        self.state = State.new

    def boot(self):
        """启动文件进程要求的操作"""
        logger.info('booting the %s' % self)
        self.state = State.running

    def kill(self, restart=True):
        logger.info('Killing %s' % self)
        """终止文件服务进程要求的操作"""
        self.state = State.restart if restart else State.zombie

    @staticmethod
    def create_file(user, name, permissions):
        """检查访问权限的有效性和用户权限等等"""
        logger.info('trying to create file %s for user %s with permissions %s' % (name, user, permissions))


class ProcessServer(Server):
    def __init__(self):
        """初始化进程服务进程要求的操作"""
        self.name = 'ProcessServer'
        self.state = State.new

    def boot(self):
        logger.info('booting the %s' % self)
        self.state = State.running

    def kill(self, restart=True):
        logger.info('killing %s' % self)

        """终止进程服务要求的操作"""
        self.state = State.restart if restart else State.zombie

    @staticmethod
    def create_process(user, name):
        """检查用户权限和生成的PID"""
        logger.info('trying to create the process %s for user %s ' % (name, user))


logger = logging.getLogger(__name__)


class OperatingSystem(object):
    """外观"""

    def __init__(self):
        self.fs = FileServer()
        self.ps = ProcessServer()

    def start(self):
        [i.boot() for i in (self.fs, self.ps)]

    def create_file(self, user, name, permissions):
        return self.fs.create_file(user, name, permissions)

    def create_process(self, user, name):
        return self.ps.create_process(user, name)


def main():
    operation_system = OperatingSystem()
    operation_system.start()
    operation_system.create_file('foo', 'hello', '-rw-r-r')
    operation_system.create_process('bar', 'ls /tmp')


if __name__ == "__main__":
    current_time = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
    logging.basicConfig(
        format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s',
        level=logging.DEBUG,
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='%s.log.%s' % (sys.argv[0], current_time)
    )
    logger.info("running %s", " ".join(sys.argv))
    program = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser()
    parser.add_argument("-output", help="")
    args = parser.parse_args()
    if args.output:
        outfile = args.output
    else:
        pass

    logger.info("finished running %s", program)

    main()
