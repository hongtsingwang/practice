#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from math import sqrt
import random
from itertools import product
import logging

reload(sys)
sys.setdefaultencoding("utf-8")

"""常用数学值的计算"""

logging.basicConfig(
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    level=logging.DEBUG,
    datefmt='%a, %d %b %Y %H:%M:%S'
)


def euclidean_metric(num1, num2):
    """
    欧几里得距离计算。详情见：https://zh.wikipedia.org/zh-hans/%E6%AC%A7%E5%87%A0%E9%87%8C%E5%BE%97%E8%B7%9D%E7%A6%BB
    :param num1:list
    :param num2:list
    :return: 欧几里得距离结果
    """
    assert len(num1) == len(num2), "the length of num1 and the length of num2 should be equal"
    return sqrt(sum([pow(num1[i] - num2[i], 2) for i in range(len(num1))]))


def pearson_correlation_score(num1, num2):
    """
    皮尔逊相关系数可以对欧几里得距离的夸大分值进行修正。
    https://zh.wikipedia.org/wiki/%E7%9A%AE%E5%B0%94%E9%80%8A%E7%A7%AF%E7%9F%A9%E7%9B%B8%E5%85%B3%E7%B3%BB%E6%95%B0
    :param num1:
    :param num2:
    :return: 皮尔逊相关系数
    """
    assert len(num1) == len(num2), "the length of num1 and the length of num2 should be equal"
    list_length = len(num1)
    sum1 = sum(num1)
    sum2 = sum(num2)
    sum1square = sum([pow(x, 2) for x in num1])
    sum2square = sum([pow(x, 2) for x in num2])
    p_sum = sum([num1[i] * num2[i] for i in list_length])

    # 相关系数的分子
    numerator = p_sum - (sum1 * sum2) / list_length
    # 分母
    denominator = sqrt(sum1square - pow(sum1, 2) / list_length) * sqrt(sum2square - pow(sum2, 2))
    result = numerator / denominator
    return result


def manhattan_distance_score(num1,num2):
    """
    曼哈顿距离计算： http://baike.baidu.com/link?url=gs6RsE_cU0n-FR3rwNvlB6OgU-D1JfgLj1PM8p3EbwPy010c6ZwIKlL6asDjAiyE-9p_0BtmqalccY6s1iDceLbwracOXgUq5WEVSox8RSZv1darHTBgBL6gkBbxCTswxKfxQt0IM5M4TQEAIdO1Rq
    :param num1: list
    :param num2: list
    :return: 曼哈顿距离结果
    """
    return sum([abs(num1[i] - num2[i]) for i in range(len(num1))])


def tanimoto_score(num1, num2):
    """
    计算两个集合的相似程度
    http://www.ibm.com/developerworks/cn/web/1103_zhaoct_recommstudy2/index.html
    :param num1:
    :param num2:
    :return:tanimoto结果
    """
    inter_set = set(num1) & set(num2)
    union_set = set(num1) | set(num2)
    return 1.0 / (len(inter_set) / len(union_set))


def multidimensional_scaling(data, distance=pearson_correlation_score, rate=0.01, iter_num=1000):
    """
    多维缩放。http://www.cnblogs.com/fengjinge/p/5181591.html. 本代码缩放为2维空间
    :param data: 数据集输入
    :param distance: 计算距离的公式
    :param rate: 移动长度比率
    :param iter_num: 迭代次数
    :return: 缩放结果
    """
    num_dimensional = len(data)

    # 计算每一对数据项之间的真实距离
    real_dist = [[distance(data[i], data[j]) for j in range(num_dimensional)] for i in range(n)]

    outer_sum = 0.0

    # 随机初始化点在二维空间之中的起始位置
    loc = [[random.random(), random.random()] for i in range(num_dimensional)]
    fake_distance = [[0.0 for j in range(num_dimensional)] for i in range(num_dimensional)]

    last_error = None
    for m in range(iter_num):
        # 寻找投影后的举例
        for i in range(num_dimensional):
            for j in range(num_dimensional):
                fake_distance[i][j] = sqrt(sum(pow(loc[i][x] - loc[j][x], 2)) for x in range(num_dimensional))

        # 移动节点
        grad = [[0.0, 0.0] for i in range(num_dimensional)]

        total_error = 0
        for j, k in product(range(num_dimensional), range(num_dimensional)):
            if k == j:
                continue
            error_term = (fake_distance[j][k] - real_dist[j][k]) / real_dist[j][k]

            # 根据误差的多少， 移动节点
            grad[k][0] += (loc[k][0] - loc[j][0]) / fake_distance[j][k] * error_term
            grad[k][1] += (loc[k][1] - loc[j][1]) / fake_distance[j][k] * error_term
            total_error += abs(error_term)
        logging.info("%d", total_error)

        # 如果节点移动之后的情况变得更糟， 那么程序就结束
        if last_error and last_error < total_error:
            break
        last_error = total_error

        for k in range(n):
            loc[k][0] -= rate * grad[k][0]
            loc[k][1] -= rate * grad[k][1]
    return loc
