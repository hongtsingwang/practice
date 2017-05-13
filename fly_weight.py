#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2016/12/17 17:45
# @Author   : Wang Hongqing
# @File     : fly_weight.py
# @Software : PyCharm

import os
import sys
import logging
import argparse
import datetime
from enum import Enum
import random

reload(sys)
sys.setdefaultencoding("utf-8")

logger = logging.getLogger(__name__)
TreeType = Enum('TreeType', 'apple_tree cherry_tree peach_tree')


class Tree(object):
    pool = dict()

    def __new__(cls, tree_type):
        obj = cls.pool.get(tree_type, None)
        if not obj:
            obj = object.__new__(cls)
            cls.pool[tree_type] = obj
            obj.tree_type = tree_type
        return obj

    def render(self, age, x, y):
        """着色"""
        logger.info("render a tree of type %s and age %s at (%s,%s)" % (self.tree_type, age, x, y))


def main():
    random_number = random.Random
    age_min, age_max = 1, 30
    min_point, max_point = 0, 100
    tree_counter = 0

    for _ in range(10):
        tree_1 = Tree(TreeType.apple_tree)
        tree_1.render(random.randint(age_min, age_max), random.randint(min_point, max_point),
                      random.randint(min_point, max_point))
        tree_counter += 1

    for _ in range(3):
        tree_1 = Tree(TreeType.cherry_tree)
        tree_1.render(random.randint(age_min, age_max), random.randint(min_point, max_point),
                      random.randint(min_point, max_point))
        tree_counter += 1

    for _ in range(5):
        tree_1 = Tree(TreeType.peach_tree)
        tree_1.render(random.randint(age_min, age_max), random.randint(min_point, max_point),
                      random.randint(min_point, max_point))
        tree_counter += 1

    logger.info("trees rendered %d" % tree_counter)
    logger.info("trees actually created %d" % (len(Tree.pool)))


if __name__ == "__main__":
    current_time = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")
    logging.basicConfig(
        format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s',
        level=logging.DEBUG,
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='%s.log.%s' % (sys.argv[0], current_time)
    )
    logging.info("running %s", " ".join(sys.argv))
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
