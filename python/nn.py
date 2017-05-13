#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===============================================================================
# 
# Copyright (c) 2017 Letv.com, Inc. All Rights Reserved
# @Time     : 2017/1/23 20:52
# @Author   : Wang Hongqing
# @File     : nn.py
#
# ===============================================================================
import os
import sys
import logging
import argparse
import datetime
from math import tanh
from sqlite3 import dbapi2 as sqlite

reload(sys)
sys.setdefaultencoding("utf-8")

current_time = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    level=logging.DEBUG,
    datefmt='%a, %d %b %Y %H:%M:%S'
)


class searchnet:
    def __init__(self, dbname):
        """

        :param dbname:
        """
        self.connect = sqlite.connect(dbname)

    def __del__(self):
        self.connect.close()

    def make_tables(self):
        self.connect.execute("create table hiddennode(create_key)")
        self.connect.execute("create table wordhidden(fromid,toid,strength)")
        self.connect.execute("create table hiddenurl(fromid,toid,strength")
        self.connect.commit()

    def get_strength(self, fromid, toid, layer):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'
        res = self.connect.execute(
            "select strength from %s where fromid=%s and toid=%s" % (table, fromid, toid)).fetchone()
        # fetchone 只取一行结果。 这个本来就只有一行 返回只有一个元组
        if not res:
            if layer == 0:
                return -0.2  # 如果库里面没有这个链接，那么返回一个默认值-0.2
            if layer == 1:
                return 0
        return res[0]  # 返回strength

    def set_strength(self, fromid, toid, layer, strength):
        """
        判断链接是否已经存在，并且利用新的强度值来更新链接或者创建链接。 该函数主要用于训练神经网络
        :param fromid:
        :param toid:
        :param layer:
        :param strength:
        :return:
        """
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'
        res = self.connect.execute(
            "select strength from %s where fromid=%s and toid=%s" % (table, fromid, toid)).fetchone()
        if not res:
            self.connect.execute("insert into %s(fromid,toid,strength) values(%d,%d,%f)" % (table, fromid, toid))
        else:
            rowid = res[0]
            self.connect.execute("update %s set strength=%f where rowid=%d" % (table, strength, rowid))

    def generate_hidden_node(self, wordids, urls):
        """
        传入一个没出现过的单词组合之中， 在隐藏层中建立新的节点， 函数会在单词与隐藏将诶点之间，以及查询节点
        和查询返回的URL之间建立具有默认权重的链接。
        :param wordids:
        :param urls:
        :return:
        """
        if len(wordids) > 3:
            return None
        create_key = "_".join(sorted([str(wi) for wi in wordids]))
        result = self.connect.execute("select rowid from hiddennode where create_key='%s'" % create_key).fetchone()

        if not result:
            cursor = self.connect.execute("insert into hiddennode (create_key) values('%s')" % create_key)
            hiddenid = cursor.lastrowid  # 返回结果的最后一行

            for wordid in wordids:
                self.set_strength(wordid, hiddenid, 0, 1.0 / len(wordids))
            for url_id in urls:
                self.set_strength(hiddenid, url_id, 1, 0.1)
            self.connect.commit()

    def get_all_hidden_ids(self, word_ids, url_ids):
        """
        查询出节点与链接的信息，然后在内存中建立起来与某项查询相关的网络
        :param word_ids:
        :param url_ids:
        :return:
        """
        l1 ={}
        for word_id in word_ids:
            cursor = self.connect.execute("select toid from wordhidden where fromid=%d"%word_id)
            for row in cursor:
                l1[row[0]] = 1

        for url_id in url_ids:
            cursor = self.connect.execute("select fromid from hiddenurl where toid=%d"%url_id)
            for row in cursor:
                l1[row[0]] = 1
        return l1.keys()

    def setup_network(self,word_ids,url_ids):
        """
        建立相应的网络
        :param word_ids:
        :param urlids:
        :return:
        """
        # 值列表
        self.word_ids= word_ids
        self.hidden_ids = self.get_all_hidden_ids(word_ids,url_ids)
        self.url_ids = url_ids

        # 建立节点输出
        self.ai = [1.0] * len(self.word_ids)
        self.ah = [1.0] * len(self.hidden_ids)
        self.ao = [1.0] * len(self.url_ids)

        # 建立权重矩阵
        self.wi = [[self.get_strength(word_id,hidden_id,0) for hidden_id in self.hidden_ids] for word_id in self.word_ids]
        self.wo = [[self.get_strength(hidden_id,url_id,0) for hidden_id in self.hidden_ids] for url_id in self.url_ids]

    def feed_forward(self):
        """
        接受一列输入，并将其推入网络
        :return:
        """
        for i in range(len(self.word_ids)):
            self.ai[i] = 1.0

        for j in range(len(self.hidden_ids)):
            sum1 = 0.0
            for i in range(len(self.word_ids)):
                sum1 = sum1 + self.ai[i] * self.wi[i][j]
            self.ah[j] = tanh(sum1)

        for k in range(len(self.url_ids)):
            sum2 = 0.0
            for j in range(len(self.hidden_ids)):
                sum2 += self.ah[j]* self.wo[j][k]
            self.ao[k] = tanh(sum2)
        return self.ao[:]

    def get_result(self,word_ids,url_ids):
        """
        建立神经网络，调用feedforward函数针对一组单词与URL给出输出
        :param word_ids:
        :param url_ids:
        :return:
        """
        self.setup_network(word_ids,url_ids)
        return self.feed_forward()

    def dtanh(self,y):
        """
        计算改变输入对输出的影响
        :param y: 输出结果
        :return:
        """
        return 1.0-y*y

    def back_propagate(self,targets,N=0.5):
        """
        后向传播算法
        :param targets:
        :param N:
        :return:
        """
        # 计算输出层的误差
        output_deltas = [0.0] * len(self.url_ids)
        for k in range(len(self.url_ids)):
            error = targets[k] - self.ao[k]
            output_deltas[k] = self.dtanh(self.ao[k])*error

        # 计算隐藏层的误差
        hidden_deltas = [0.0] * len(self.hidden_ids)
        for j in range(len(self.url_ids)):
            error = 0.0
            for k in range(self.url_ids):
                error += output_deltas*self.wo[j][k]
            hidden_deltas[j] = self.dtanh(self.ah[j]) * error

        # 更新输出权重
        for j in range(len(self.hidden_ids)):
            for k in range(len(self.url_ids)):
                change = output_deltas[k] * self.ah[j]
                self.wo[j][k] += N * change

        for i in range(len(self.word_ids)):
            for j in range(len(self.hidden_ids)):
                change = hidden_deltas[j]*self.ai[i]
                self.wi[i][j] += N * change

    def train_frequency(self,word_ids,url_ids,selected_url):
        """
        建立神经网络，进行后向传播算法的训练
        :param word_ids:
        :param url_ids:
        :param selected_url:
        :return:
        """
        self.generate_hidden_node(word_ids,url_ids)

        self.setup_network(word_ids,url_ids)
        self.feed_forward()
        targets = [0.0] * len(url_ids)
        targets[url_ids.index(selected_url)] = 1.0
        self.back_propagate(targets)
        self.update_database()

    def update_database(self):
        """
        将结果存在数据库之中
        :return:
        """
        for i in range(len(self.word_ids)):
            for j in range(len(self.hidden_ids)):
                self.set_strength(self.word_ids[i],self.hidden_ids[j],0,self.wi[i][j])
        for j in range(len(self.hidden_ids)):
            for k in range(len(self.url_ids)):
                self.set_strength(self.hidden_ids[j],self.url_ids[k],1,self.wo[j][k])
        self.connect.commit()

