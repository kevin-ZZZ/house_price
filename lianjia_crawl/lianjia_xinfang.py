# 链家网房价数据
# coding:utf-8
from .baseinfo import Base
import requests
from lxml import etree
import re
import json
import time


class Lianjia_xinfang(object):

    def parse_city(self, context):
        """
        响应解析后的html页面（此函数用于获取城市网站的链接）
        :param context:
        :return:
        """
        html = etree.HTML(context)
        nodes = html.xpath('//li[@class="clear"]/div/a')
        print(nodes)
        city_dict = {}
        for node in nodes:
            city_link = node.xpath('./@href')[0]
            city_name = node.xpath('./text()')[0]
            # print(city_link, city_name)
            city_dict.update({city_name: city_link})
        # print(city_dict)
        return city_dict

    def parse_house_url(self, city_dict):
        """
        解析每个地区房地产公司的详细信息，房价/小区
        :param context:
        :return:
        """
        lianjia_house_dict = {}
        pattern = re.compile(r'^https')
        pattern2 = re.compile(r'^https://hk')
        for key, value in city_dict.items():
            result = pattern.match(value)
            result2 = pattern2.match(value)
            if result and not result2:
                # 将平常的链家网址提取json数据操作
                content_info = self.solve_json(value)
            else:
                # 将特殊的网址（链家旅居网）进行特殊处理
                pass
            lianjia_house_dict.update({key: content_info})
            time.sleep(0.5)
        return lianjia_house_dict

    def solve_json(self, url):
        """
        将传入的json数据进行重新整理
        :param json:
        :return:
        """
        url += 'loupan/mapsearch/resblock?&'
        context = self.send_request(url).text
        # print(type(context))
        context_format = str(context).replace('null', '""')
        try:
            content = json.loads(context)
        except:
            print(url)
            print(context)

        # 重新整理数据结构
        house_data = content["data"]
        # print(house_data)
        # print(len(house_data.items()))
        if not house_data:
            return None
        distinct_list = {}
        for key, value in house_data.items():
            for i in value:
                house_price = i.get("show_price", "暂无报价") if i.get("show_price", "暂无报价") else "暂无报价"
                house_name = i.get("resblock_name", None)
                resblock_frame_area = i.get("resblock_frame_area", "暂无户型详情")
                house_type = i.get("house_type", None)
                if i["district_name"] in distinct_list.keys():
                    distinct_list[i["district_name"]].append(
                        {house_name: [house_price, resblock_frame_area, house_type, i["district_name"]]})
                else:
                    distinct_list.update(
                        {i["district_name"]: [
                            {house_name: [house_price, resblock_frame_area, house_type, i["district_name"]]}, ]})
        print(distinct_list)
        return distinct_list

    def write_file(self, info):
        info = json.dumps(info)
        with open('./全国链家新房均价.Json', 'w')as f:
            f.write(info)
            f.close()
        print("write_down")


if __name__ == '__main__':
    lianjia = Lianjia_xinfang()
    url = 'https://hui.lianjia.com/'
    context = lianjia.send_request(url).text
    city_dict = lianjia.parse_city(context)
    house_info_full = lianjia.parse_house_url(city_dict)
    lianjia.write_file(house_info_full)
