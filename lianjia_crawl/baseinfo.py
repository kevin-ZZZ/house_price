# coding:utf-8
"""
@project:
@author:
@file:
@ide:
@time:
@description：将公共方法提取到这个文件中
"""

import requests
from lxml import etree
import time
from bs4 import BeautifulSoup
import threading


class Base(object):

    def send_request(self, url, proxies=None, timeout=5):
        """
        封装发送请求模块
        :param url:
        :return:
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        for i in range(5):
            try:
                context = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
                if context.status_code == 200:
                    return context
            except Exception as e:
                print(e)
        else:
            print("[WARNING]:GET NO RESPONSE FROM THIS URL:%s\n" % url, )
        # return requests.get(url, headers=headers, proxies=proxies)


class Proxy(object):
    """
    获取网上的免费代理
    """

    def __init__(self):
        """
        将一些常用的属性定义在这里
        """
        self.request = Base()

    def get_proxy(self):
        """
        获取免费代理
        :return:
        """
        xicidaili_dict = self.get_xicidaili_proxy()
        ip_port_dict = self.get_kuaidaili_proxy()
        ip_port_dict.update(xicidaili_dict)

        proxy_list = []
        for key, value in ip_port_dict.items():
            proxy_list.append({value: key})
        print(proxy_list)
        worked_proxy = self.test_proxy(proxy_list)
        print(worked_proxy)
        return worked_proxy

    def get_kuaidaili_proxy(self):
        """
        从快代理网站获取代理
        :return:
        """
        ip_port_dict = {}
        base_url = 'https://www.kuaidaili.com/free/inha/'
        url_list = [base_url + str(i) + '/' for i in range(1, 5)]
        for url in url_list:
            # print(url)
            html = self.request.send_request(url).text
            if not html:
                print("没有获取到页面！")
            content = etree.HTML(html)
            nodes = content.xpath('//div[@id="content"]//tbody/tr')
            # print(nodes)
            for node in nodes:
                http_type = node.xpath('./td/text()')[3]
                ip = node.xpath('./td/text()')[0]
                port = node.xpath('./td/text()')[1]
                ip_port_dict.update({http_type.lower() + '://' + ip + ':' + port: http_type.lower()})
                time.sleep(0.1)
        return ip_port_dict

    def get_xicidaili_proxy(self):
        """
        从西刺代理获取免费代理
        :return:
        """
        ip_port_dict = {}
        base_url = 'http://www.xicidaili.com/nn/'
        url_list = [base_url + str(i) + '/' for i in range(1, 5)]
        for url in url_list:
            # print(url)
            html = self.request.send_request(url).text
            # print(html)
            if not html:
                print("没有获取到页面！")
            # content = etree.HTML(html)
            # nodes = content.xpath('//div[@id="wrapper"]//tbody/tr')
            # print(nodes)
            soup = BeautifulSoup(html, 'lxml')
            soup1 = soup.find(attrs={"id": "ip_list"})
            nodes = soup1.find_all('tr')[1:]
            for node in nodes:
                info = node.find_all('td')
                ip = info[1].get_text()
                port = info[2].get_text()
                http_type = info[5].get_text()
                ip_port_dict.update({http_type.lower() + '://' + ip + ':' + port: http_type.lower()})
                time.sleep(0.1)
            # print(ip_port_dict)
        return ip_port_dict

    def test_proxy(self, proxy_list):
        """
        对传入的免费代理进行测试
        :param proxy_list:
        :return:
        """
        worked_proxy_list = []
        for proxy in proxy_list:
            print(proxy)
            response = self.request.send_request("https://www.baidu.com", proxies=proxy, timeout=2)
            if response and response.status_code == 200:
                worked_proxy_list.append(proxy)
        return worked_proxy_list


if __name__ == '__main__':
    proxy = Proxy()
    proxy.get_proxy()
