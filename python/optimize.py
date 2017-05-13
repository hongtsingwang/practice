#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===============================================================================
# 
# Copyright (c) 2017 Letv.com, Inc. All Rights Reserved
# @Time     : 2017/2/2 21:00
# @Author   : Wang Hongqing
# @File     : optimize.py
#
# ===============================================================================
import os
import sys
import logging
import argparse
import datetime
import random
import math

reload(sys)
sys.setdefaultencoding("utf-8")

current_time = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    level=logging.DEBUG,
    datefmt='%a, %d %b %Y %H:%M:%S'
)


def random_optimize(domain, cost_function):
    """
    随机搜索算法，所有算法的baseline. 非常的低效
    :param domain: 二维数组， domain[i][0] 为下限， domain[i][1] 为上限
    :param cost_function: 计算损失的函数
    :return:
    """
    best = 999999999
    best_result = None
    for i in range(1000):
        # 创建一个随机结果
        r = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
        cost = cost_function(r)

        # 与当前的最优解进行比较
        if cost < best:
            best = cost
            best_result = r
    return best_result


def hill_climb(domain, cost_function):
    """
    爬山法计算最优点。该算法极其容易陷入局部范围的最小值
    :param domain:
    :param cost_function:
    :return:
    """
    # 创建初始随机解
    sol = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

    while True:
        # 创建相邻解的列表
        neighbors = []
        for j in range(len(domain)):
            # 在每个方向上面相对于原值偏离一点
            if sol[j] > domain[j][0]:
                neighbors.append(sol[:j] + [sol[j] - 1] + sol[j + 1:])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[:j] + [sol[j] + 1] + sol[j + 1:])
        current = cost_function(sol)
        best = current
        for j in range(len(neighbors)):
            cost = cost_function(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]
        if current == best:
            break
    return sol


def annealing_optimize(domain, cost_function, T=100000.0, cool=0.95, step=1):
    """
    模拟退火算法
    :param domain:
    :param cost_function:
    :param T:
    :param cool:
    :param step:
    :return:
    """
    vec = [float(random.randint(domain[i][0], domain[i][1])) for i in range(len(domain))]
    while T > 0.1:
        # 选择一个索引值
        i = random.randint(0, len(domain) - 1)

        # 选择一个改变索引值的方向
        direction = random.randint(-1 * step, step)

        # 创建一个新的题解的新列表，改变其中一个值
        vecb = vec[:]
        vecb += direction
        if vecb[i] < domain[i][0]:
            vecb[i] = domain[i][0]
        elif vecb[i] > domain[i][1]:
            vecb[i] = domain[i][1]

        # 计算当前成本和新的成本
        ea = cost_function(vec)
        eb = cost_function(vecb)

        # 它是最好的解吗？ 或者是趋向最优解的可能的临界解吗？
        if eb < ea or random.random < pow(math.e, -(eb - ea) / T):
            vec = vecb
        T *= cool
    return vec


def genetic_optimize(domain, cost_function, popsize=50, step=1, mutprob=0.2, elite=0.2, maxiter=100):
    """
    遗传算法
    :param domain:
    :param cost_function:
    :param popsize:
    :param step:
    :param mutprob:
    :param elite:
    :param maxiter:
    :return:
    """

    def mutate(vec):
        """
        变异操作
        :param vec:
        :return:
        """
        i = random.randint(0, len(domain) - 1)
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[0:i] + [vec[i] + step] + vec[i + 1:]

    def cross_over(r1, r2):
        """
        交叉操作
        :param r1:
        :param r2:
        :return:
        """
        i = random.randint(1, len(domain) - 2)
        return r1[:i] + r2[i:]

    # 构造初始种群
    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
        pop.append(vec)

    # 计算每一代中有多少胜出者
    top_elite = int(elite * popsize)

    for i in range(maxiter):
        scores = [(cost_function(v), v) for v in pop]
        scores.sort()
        ranked = [v for (s, v) in scores]

        # 从纯粹的胜出者开始
        pop = ranked[:top_elite]

        # 添加变异和配对之后的胜出者
        while len(pop) < popsize:
            if random.random() < mutprob:
                c = random.randint(0, top_elite)
                pop.append(mutate(ranked[c]))
            else:
                c1 = random.randint(0, top_elite)
                c2 = random.randint(0, top_elite)
                pop.append(cross_over(ranked[c1], ranked[c2]))
        logging.info("%d" % scores[0][0])
    return scores[0][1]
