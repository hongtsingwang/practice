#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===============================================================================
# 
# Copyright (c) 2017 Letv.com, Inc. All Rights Reserved
# @Time     : 2017/1/22 22:21
# @Author   : Wang Hongqing
# @File     : searcher.py
#
# ===============================================================================
import os
import sys
import logging
import argparse
import datetime
import sqlite3
import nn

reload(sys)
sys.setdefaultencoding("utf-8")

current_time = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    level=logging.DEBUG,
    datefmt='%a, %d %b %Y %H:%M:%S'
)

my_net = nn.searchnet("nn.db")

class searcher:
    def __init__(self, dbname):
        """
        初始化
        :param dbname:数据库名称
        """
        self.connect = sqlite3.connect(dbname)

    def __del__(self):
        self.connect.close()

    def dbcommit(self):
        self.connect.commit()

    def get_match_rows(self, q):
        """
        构造查询的字符串
        :param q:
        :return:
        """
        filed_list = 'w0.url_id'
        table_list = ''
        clause_list = ''  # clause: 分句
        word_ids = []

        # 根据空格拆分单词
        words = q.split(' ')
        table_number = 0

        for word in words:
            word_row = self.connect.execute("select row_id from word_list where word='%s'" % word).fetchone()
            if word_row:
                word_id = word_row[0]
                word_ids.append(word_id)
                if table_number > 0:
                    table_list += ","
                    clause_list += ' and '
                    clause_list += 'w%d.url_id=w%d.url_id and ' % (table_number - 1, table_number)
                filed_list += ',w%d.location' % table_number
                table_list += 'word_location w %d' % table_number
                clause_list += 'w%d.wordid=%d' % (table_number, word_id)
                table_number += 1

            # 根据各个组分， 建立查询
            full_query = 'select %s from %s where %s' % (filed_list, table_list, clause_list)
            cursor = self.connect.execute(full_query)
            rows = [row for row in cursor]

            return rows, word_ids

    def get_score_list(self, rows, word_ids):
        """
        接收查询请求，将获取到的行集置于字典之中，并且以格式化的形式显示输出
        :param rows:
        :param word_ids:
        :return:
        """
        total_scores = dict.fromkeys(rows)
        weights = [(1.0, self.normalize_scores(rows)), (1.5, self.location_score(rows))]

        for (weight, scores) in weights:
            for url in total_scores:
                total_scores[url] += weight * scores[url]
        return total_scores

    def get_url_name(self, id):
        return self.connect.execute("select url from url_list where rowid=%d" % id).fetchone()[0]

    def query(self, q):
        rows, word_ids = self.get_match_rows(q)
        scores = self.get_score_list(rows, word_ids)
        ranked_score = sorted([(score, url) for (url, score) in scores.items()], reverse=True)
        for (score, url_id) in ranked_score[0:10]:
            print '%f\t%s' % (score, self.get_url_name(url_id))
        return word_ids,[r[1] for r in ranked_score[0:10]]

    def normalize_scores(self, scores, small_is_better=True):
        """

        :param scores:
        :param small_is_better:
        :return:
        """
        vsmall = 0.00001  # 此值的作用是避免被0整除
        if small_is_better:
            min_score = min(scores.values())
            return dict([(u, float(min_score) / max(vsmall, 1)) for (u, l) in scores.items()])
        else:
            max_score = max(scores.values)
            if max_score == 0:
                max_score = vsmall
                return dict([(u, float(c) / max_score) for (u, l) in scores.items()])

    def frequency_score(self, rows):
        counts = dict([(row[0], 0) for row in rows])
        for row in rows:
            counts[row[0]] += 1
        return self.normalize_scores(counts)

    def location_score(self, rows):
        """
        根据单词在文档中所处的位置给文档排序， 通常，单词出现的越靠前， 这篇文章和查询的单词的相关性越高。
        :param rows:
        :return:
        """
        location = dict([(row[0], 1000000) for row in rows])
        for row in rows:
            loc = sum(row[1:])
            if loc < location[row[0]]:
                location[row[0]] = loc

        return self.normalize_scores(location, small_is_better=True)

    def distance_score(self, rows):
        if len(rows[0]) <= 2:
            return dict([(row[0], 1.0) for row in rows])

        min_distance = dict([(row[0], 1000000000) for row in rows])

        for row in rows:
            dist = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
            if dist < min_distance[row[0]]:
                min_distance[row[0]] = dist
        return self.normalize_scores(min_distance, small_is_better=True)

    def inboundlink_score(self, rows):
        unique_urls = set([row[0] for row in rows])
        inbound_count = dict([(u, self.connect.execute(
            "select count(*) from link where toid=%d" % u).fetchone()[0])
                              for u in unique_urls])
        return self.normalize_scores(inbound_count)

    def calculate_pagerank(self,iterations=20):
        """
        计算pagerank
        :param iterations: 最高迭代次数
        :return:
        """
        # 清除当前的pagerank表
        self.connect.execute("drop table if exists pagerank")
        self.connect.execute("create table pagerank(urlid primary key, score)")

        # 初始化url
        self.connect.execute("insert into pagerank select rowid,1.0 from urllist")
        self.dbcommit()
        for i in range(iterations):
            logging.info("Iteration %d"%i)
            for (urlid,) in self.connect.execute("select rowid from urllist"):
                pr=0.15
                for (linker,) in self.connect.execute("select distinct fromid from link where toid = %d"%urlid):
                    linking_pr = self.connect.execute("select score from pagerank where urlid=%d"%linker).fetchone()[0]

                    # 得到总的连接数
                    linking_count = self.connect.execute("select count(*) from link where fromid=%d"%linker).fetchone()[0]
                    pr += 0.85 * (linking_pr / linking_count)
                self.connect.execute("update pagerank set score=%f where urlid=%d"%(pr,urlid))
                self.dbcommit()

    def pagerank_score(self,rows):
        pageranks = dict([(row[0], self.connect.execute("select score from pagerank where urlid=%d"%row[0]).fetchone()[0]) for row in rows])
        max_rank = max(pageranks.values())
        normalized_scores = dict([(u, float(l)/max_rank) for (u,l) in pageranks.items()])
        return normalized_scores

    def link_text_score(self,rows,wordids):
        link_scores = dict([(row[0],0) for row in rows])
        for wordid in wordids:
            cursor = self.connect.execute("select link.fromid,link.toid from linkwords,link where wordid=%d and linkwords.linkid=link.rowid"%wordid)
            for (fromid,toid) in cursor:
                if toid in link_scores:
                    pr = self.connect.execute("select score from pagerank where urlid=%d"%fromid).fetchone()[0]
                    link_scores[toid] += pr
        max_score = max(link_scores.values())
        nornamlize_score = dict([(u,float(l)) for (u,l) in link_scores.items()])
        return nornamlize_score


    def nn_score(self, rows, word_ids):
        """
        用神经网路的方法对结果进行加权处理
        :param rows:
        :param word_ids:
        :return:
        """
        url_ids = [url_id for url_id in set([row[0] for row in rows])]
        nn_result = my_net.get_result(word_ids,url_ids)
        scores = dict([(url_ids[i],nn_result[i]) for i in range(len(url_ids))])
        return self.normalize_scores(scores)



