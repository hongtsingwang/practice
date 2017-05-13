#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===============================================================================
# 
# Copyright (c) 2017 Letv.com, Inc. All Rights Reserved
# @Time     : 2017/1/22 9:33
# @Author   : Wang Hongqing
# @File     : crawlers.py
#
# ===============================================================================
import os
import sys
import logging
import argparse
import datetime
import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin
import sqlite3

reload(sys)
sys.setdefaultencoding("utf-8")

current_time = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    level=logging.DEBUG,
    datefmt='%a, %d %b %Y %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.info("running %s", " ".join(sys.argv))

class crawler(object):
    def __init__(self,dbname=None):
        """
        爬虫基类初始化
        :param dbname:  爬虫载入的数据库的名称
        """
        self.connect = sqlite3.connect(database=dbname)

    def __del__(self):
        self.connect.close()
        pass

    def dbcommit(self):
        self.connect.commit()
        pass

    def get_entry_id(self,table,field,value,create_new=True):
        """
        辅助函数， 用于获取条目的id, 并且如果条目不存在， 就将其加入到数据库之中。
        :param table: 表的名称
        :param field:  要取的字段
        :param value:  获取value
        :param create_new: 是否要把不存在的结果加入到数据库之中
        :return:
        """
        return None

    def add_to_index(self,url,soup):
        """
        为每个网页建立索引
        :param url: 网址
        :param soup:
        :return:
        """
        logging.info("indexing %s"%url)

    def get_text_only(self,soup):
        """
        从一个HTML网页之中提取不带标签的文字
        :param soup: BeatifulSoup 对象
        :return: 提取文字的结果
        """
        return None

    def separate_words(self, text):
        """
        根据任何非空白字符进行分词处理
        :param text: 输入文本
        :return:  分词结果
        """
        return None

    def is_indexed(self,url):
        """
        判定该网页是否被建过索引，如果建过， 就返回True
        :param url: 网址
        :return: True or False
        """
        return False

    def add_link_ref(self,url_from, url_to, link_text):
        """
        添加一个关联两个网页的链接
        :param url_from:
        :param url_to:
        :param link_text:
        :return:
        """
        pass

    def crawl(self,pages,depth=2):
        """
        从一个小组网页开始进行广度优先搜索，直到达到深度 为网页建立索引。
        :param pages:
        :param depth:
        :return:
        """
        for i in range(depth):
            new_pages = set()
            for page in pages:
                try:
                    page_open = urllib2.urlopen(page)
                except:
                    logging.error("could not open %s"%page)
                soup = BeautifulSoup(page_open.read())
                self.add_to_index(page,soup=soup)

                links = soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url = urljoin(page,link['href'])
                        if url.find("'") != -1:
                            # 网页链接里是不能有引号的，如果有引号，说明是不合法的网址
                            continue
                        url = url.split("#")[0]
                        if url[0:4]== 'http' and not self.is_indexed(url):
                            new_pages.add(url)
                        link_text = self.get_text_only(link)
                        self.add_link_ref(page, url, link_text)
        pass

    def create_index_tables(self):
        """创建数据表"""
        self.connect.execute("create table urllist(url)")
        self.connect.execute("create table wordlist(word)")
        self.connect.execute("create table wordlocation(urlid, wordid, location)")
        self.connect.execute("create table link(fromid integet, toid integer)")
        self.connect.execute("create table linkwords(wordid,linkid)")
        self.connect.execute("create index wordidx on wordlist(word)")
        self.connect.execute("create index urlidx on urllist(url)")
        self.connect.execute("create index wordurlidx on wordlocation(wordid)")
        self.connect.execute("create index urltoinx on link(toid)")
        self.connect.execute("create index urlfromidx on link(fromid)")
        self.dbcommit()
        pass


