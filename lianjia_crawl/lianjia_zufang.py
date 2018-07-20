# coding:utf-8
"""
@project:
@author: kevin
@file:
@ide: pycharm
@time: 2018年7月17号
@description:
    链家租房主页（城市.lianjia.com/zufang/）,由于链家的列表页面无法提取出最大页面数，故无法直接使用url拼接
    但是其实在页面的右上角会显示总共搜索到的房子数量，除以每张详情页面的房子数，即可以提取到页面数，另外，链
    家最大的显示数量为100*30条数据，多出来的是不可能的通过翻页实现的。
    所以逻辑为：将整体划分为小块，根据筛选条件划分为个体小于3000的符合要求的网址，然后进行页面爬取

"""
from .baseinfo import Base
import requests
from lxml import etree
import re
import time
import json
from .baseinfo import Proxy


class Lianjia_zufang(Base):


    def parse_html(self, html):
        """
        解析最开始的列表页，提取并划分为小块，取出网址
        :return:
        """
        content = etree.HTML(html)
        nodes = content.xpath('//dd[@data-index="1"]/div[@class="option-list"]/a')
        print("number_list", nodes)

        # 将分块网址与金额划分相关联，存储在字典中，防止出现分块的数量仍然大于3000
        node_url_dict = {}
        pattern = re.compile(r'\d+')
        for node in nodes:
            node_link = node.xpath('./@href')[0]
            node_number = node.xpath('./text()')[0]
            number_list = pattern.findall(node_number)
            if not number_list:
                continue
            number_list = [int(i) for i in number_list]
            link = 'https://sz.lianjia.com' + node_link
            node_url_dict.update({link: number_list})
        print(node_url_dict)
        return node_url_dict

    def get_part_html(self, url_dict):
        """
        将划分好的列表页按照{url:etree.HTML(html)} 打包，发送给其它函数解析
        :param url_dict:
        :return:
        """
        content_url_dict = {}
        for url, value in url_dict.items():
            html = self.send_request(url).text
            content = etree.HTML(html)
            total_number = content.xpath('//div[@class="main-box clear"]/div[@class="con-box"]//h2/span//text()')[0]
            # print(total_number)
            if int(total_number) > 3000 and len(value) > 1:
                # 此处进行单页大于3000条数据的操作
                # middle = sum(value) / len(value)
                pass
            else:
                content_url_dict.update({url: content})
                number = int(total_number) // 30 + 1
                for x in range(1, number + 1):
                    # 先将url拼接成为类似  https://sz.lianjia.com/zufang/rp7/  的形式
                    if x == 1:
                        continue
                    str_comb = 'zufang/' + 'pg' + str(x)
                    single_url = str_comb.join(url.split('zufang/'))
                    single_html = self.send_request(single_url).text
                    single_cont = etree.HTML(single_html)
                    content_url_dict.update({single_url: single_cont})
                    time.sleep(0.2)
            print(len(content_url_dict))
        # print (content_url_dict)
        return self.parse_part_content(content_url_dict)

    def parse_part_content(self, content_url_dict):
        """
        解析字典里面的列表页，将详情页的网址保存到字典，以供后续使用
        :return:
        """
        # 用字典来存储详细房屋的信息
        info_dict = {}
        pattern = re.compile(r'\d{12}')
        for key, value in content_url_dict.items():
            nodes = value.xpath('//div[@class="wrapper"]//div[@class="list-wrap"]/ul/li')
            for node in nodes:
                # print(key, value)
                house_judge = node.xpath('.//div[@class="where"]/a/@href')
                if not house_judge:
                    continue
                house_links = house_judge[0]
                try:
                    house_locat = node.xpath('.//div[@class="where"]/a/span/text()')[0]
                except:
                    house_locat = None
                try:
                    house_types = node.xpath('.//div[@class="where"]/span[1]/span/text()')[0]
                except:
                    house_types = None
                try:
                    house_squar = node.xpath('.//div[@class="where"]/span[2]/text()')[0]
                except:
                    house_squar = None
                try:
                    house_orien = node.xpath('.//div[@class="where"]/span[3]/text()')[0]
                except:
                    house_orien = None
                try:
                    lian_apartm = node.xpath('.//div[@class="other"]/div[@class="con"]/a/text()')[0]
                except:
                    lian_apartm = None
                try:
                    build_total = node.xpath('.//div[@class="other"]/div[@class="con"]/text()')[0]
                except:
                    build_total = None
                try:
                    built_years = node.xpath('.//div[@class="other"]/div[@class="con"]/text()')[1]
                except:
                    built_years = None
                try:
                    house_price = node.xpath('.//div[@class="price"]/span/text()')[0]
                except:
                    house_price = None
                try:
                    update_time = node.xpath('.//div[@class="price-pre"]/text()')[0]
                except:
                    update_time = None
                try:
                    person_look = node.xpath('.//div[@class="square"]//span/text()')[0]
                except:
                    person_look = None
                try:
                    house_trans = node.xpath('.//div[@class="chanquan"]//span[@class="fang-subway-ex"]/text()')[0]
                except:
                    house_trans = None

                dict_key = pattern.findall(house_links)[0]
                info_dict.update({dict_key: {
                    "小区名称": house_locat,
                    "房屋户型": house_types,
                    "房屋链接": house_links,
                    "租金价格": house_price,
                    "房屋面积": house_squar,
                    "详细信息": {
                        "房屋朝向": house_orien,
                        "链家分部": lian_apartm,
                        "更新时间": update_time,
                        "房屋建造时间": built_years,
                        "房屋高度": build_total,
                        "看房人数": person_look
                    }}})

        return repr(info_dict)

    def persistance_save(self, info):
        """
        对信息进行持久化存储
        :param info:
        :return:
        """
        with open("./深圳租房.txt", "w") as f:
            f.write(info)
            f.close()


if __name__ == '__main__':
    # lianjia = Lianjia_zufang()
    # url = 'https://sz.lianjia.com/zufang/'
    # content = lianjia.send_request(url).text
    # node_url_dict = lianjia.parse_html(content)
    # info = lianjia.get_part_html(node_url_dict)
    # print(type(info))
    # lianjia.persistance_save(info)
    proxy = Proxy()
    proxy.get_proxy()
