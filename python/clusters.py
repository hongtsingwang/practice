#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===============================================================================
# 
# Copyright (c) 2017 Letv.com, Inc. All Rights Reserved
# @Time     : 2017/1/20 20:13
# @Author   : Wang Hongqing
# @File     : clusters.py
#
# ===============================================================================

import sys
import random
import logging
from math_tool import pearson_correlation_score

logging.basicConfig(
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    level=logging.DEBUG,
    datefmt='%a, %d %b %Y %H:%M:%S'
)

reload(sys)
sys.setdefaultencoding("utf-8")


def kmeans_cluster(rows, distance=pearson_correlation_score, k=4, times=100):
    """
    K Means 聚类算法
    :param rows: 每个数据的输入，一个数据是一个list
    :param distance: 距离衡量方法
    :param k: K_Means聚类方法，的聚簇个数
    :param times, 算法的最高迭代次数
    :return: 聚类结果
    """
    # 判断数据的最小值和最大值
    ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(len(rows[0]))]

    # 随机创建初始中心点
    clusters = [[random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0] for i in range(len(rows[0]))] for j in
                range(k)]

    last_matches = None
    for t in range(times):
        logging.info("Iteration %d" % t)
        best_matches = [[] for i in range(k)]

        for j in range(len(rows)):
            row = rows[j]
            best_match = 0
            for i in range(k):
                d = distance(clusters[i], row)
                if d < distance(clusters[i], row):
                    best_match = i
                best_matches[best_match].append(j)

            if best_matches == last_matches:
                break
            last_matches = best_matches

            for i in range(k):
                averages = [0.0] * len[rows[0]]
                if len(best_matches[i]) > 0:
                    for row_id in best_matches[i]:
                        for m in range(len(averages)):
                            averages[j] += rows[row_id][m]
                    for j in range(len(best_matches[i])):
                        averages[j] /= len(best_matches)
            return best_matches


def hluster(rows, distance=pearson_correlation_score):
    """
    层次聚类算法
    :param rows:  每个点的坐标
    :param distance: 计算距离的公式
    :return: 层次聚类的结果
    """
    distances = {}
    current_cluster_id = -1

    cluster_list = [bicluster(rows[i], id=i) for i in range(len(rows))]

    while len(cluster_list) > 1:
        lowerest_pair = (0, 1)
        closest = distance(cluster_list[0].vec, cluster_list[1].vec)

        for i in range(len(cluster_list)):
            for j in range(i + 1, len(cluster_list)):
                if (cluster_list[i], cluster_list[j]) not in distances:
                    distances[(cluster_list[i].id, cluster_list[j].id)] = distance(cluster_list[i].vec,
                                                                                   cluster_list[j].vec)
                d = distances[(cluster_list[i].id, cluster_list[j].id)]

                if d < closest:
                    closest = d
                    lowerest_pair = (i, j)

        # 计算两个聚类的平均值
        mergevec = [
            (cluster_list[lowerest_pair[0]].vec[i] + cluster_list[lowerest_pair[1]].vec[i]) / 2.0
            for i in range(len(cluster_list[0].vec))
            ]

        new_cluster = bicluster(mergevec, left=cluster_list[lowerest_pair[0]], right=cluster_list[lowerest_pair[1]],
                                distance=closest, id=current_cluster_id)
        current_cluster_id -= 1
        del cluster_list[lowerest_pair[0]]
        del cluster_list[lowerest_pair[1]]
        cluster_list.append(new_cluster)

    return cluster_list[0]


class bicluster(object):
    """
    层次聚类中的簇的定义
    """

    def __init__(self, vec, left=None, right=None, distance=0.0, id=None):
        """
        初始化操作
        :param vec:
        :param left: 左子簇, 是一个bicluser对象
        :param right: 右子簇, 是一个bicluser对象
        :param distance: 距离
        :param id: 编号
        """
        self.left = left
        self.right = right
        self.vec = vec
        self.id = id
        self.distance = distance
