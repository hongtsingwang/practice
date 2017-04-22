# -*- coding:utf-8 -*-
# @FileName  : weather_api.py
# @Author    : Wang Hongqing
# @Date      : 2017-04-22 18:09
# --------------------------------------------------------

import os
import sys
import argparse
import logging
import requests
import json

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    level=logging.DEBUG,
    datefmt='%a, %d %b %Y %H:%M:%S'
)


class Weather(object):
    def __init__(self):
        """
        weathre api
        """
        self.url = 'http://www.zuimeitianqi.com/zuimei/queryWeather'
        self.headers = dict()
        self.headers['User-Agent'] = """{
            "Cookie": "U_TRS1=000000f2.a4057b91.56df9efc.36c71881; U_TRS2=000000f2.a4137b91.56df9efc.46fde13e",
            "Referer": "http://www.baidu.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
            """
        city_id_list = [(u"成都", '01012703'), (u"杭州", "01013401"), (u"深圳", "01013401"), (u"广州", "01010704"),
                        (u"北京", "01010101"), (u"上海", "01012601")]
        self.city_list = dict()
        for item in city_id_list:
            city_name = item[0]
            city_code = item[1]
            self.city_list[city_name] = city_code
        self.actual_weather = dict()
        self.air_pollution_rate = dict()
        self.forecast_weather = dict()

    def query(self, city=u"北京"):
        """
        根据输入的城市，返回对应的天气
        :param city: 城市名称
        :return: 天气结果
        """
        if city not in self.city_list:
            print "该城市，暂时为收录"
            return
        params = {"cityCode": self.city_list[city]}
        response = requests.get(self.url, params=params)
        response_dict = json.loads(response.text)["data"][0]

        self.actual_weather = response_dict["actual"]
        self.air_pollution_rate = response_dict["air"]
        self.forecast_weather = response_dict["forecast"]
        self._actual_information(city)

    def _actual_information(self, city):
        """
        返回当下温度
        :param city: 
        :return: 
        """
        high_temperature = self.actual_weather["high"]
        low_temperature = self.actual_weather["low"]
        current_temperature = self.actual_weather["tmp"]
        today_weather = self.actual_weather["wea"]
        air_description = self.actual_weather["desc"]

        print "'%s: %s~%s°C 现在温度 %s°C 湿度：%s %s" % (
            city, low_temperature, high_temperature, current_temperature, today_weather, air_description)

def main():
    weather_api = Weather()
    weather_api.query(u'北京')

if __name__ == '__main__':
    main()
