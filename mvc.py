#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2016/12/17 19:14
# @Author   : Wang Hongqing
# @File     : mvc.py
# @Software : PyCharm

import os
import sys
import logging
import argparse
import datetime

reload(sys)
sys.setdefaultencoding("utf-8")

quotes = ('a', 'b', 'c', 'd')

class QuoteModel:
    def get_quote(self, n):
        try:
            value = quotes[n]
        except IndexError as err:
            value = 'Not Found'
        return value

class QuoteTerminalView:
    @staticmethod
    def show(self, quote):
        logger.info("the quote is %s" % (quote))

    @staticmethod
    def error(self, msg):
        logger.info("error:%s" % (msg))

    @staticmethod
    def select_quote(self):
        return input("which quote number would you like to see?")


class QuoteTerminalController:
    def __init__(self):
        self.model = QuoteModel()
        self.view = QuoteTerminalView()

    def run(self):
        valid_input = False
        while not valid_input:
            n = self.view.select_quote()
            try:
                n = int(n)
            except ValueError as err:
                self.view.error("Incorrect index %s" % (n))
            else:
                valid_input = True
        quote = self.model.get_quote(n)
        self.view.show(quote)


logger = logging.getLogger(__name__)


def main():
    controller = QuoteTerminalController()
    while True:
        controller.run()


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
