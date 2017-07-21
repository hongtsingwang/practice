#!/usr/bin/env python
# coding=utf-8

import cv2
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf8')

"""
检测图片的尺寸, 输入图片的网址， 可以获得图片的宽度和高度
"""

def downloadImg(img_url, filepath):
    try:
        r = requests.get(img_url, timeout=3)
        with open(filepath, "wb") as code:
            code.write(r.content)
    except:
        with open(filepath, "wb") as code:
            code.write("")

def imgHandler(img_url):
    fn="temp.jpg"
    downloadImg(img_url, fn)
    try:
        img = cv2.imread(fn)
        sp = img.shape
    except:
        return 0, 0
    return sp[1], sp[0]

def test():
    test_url = "http://cms-bucket.nosdn.127.net/a10fa528922d4fb29227085556af343c20170316144512.jpeg"
    width, height = imgHandler(test_url)
    print "width is %d" % width
    print "height is %d" % height


if __name__ == '__main__':
    test()
