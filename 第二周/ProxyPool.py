import requests
from bs4 import BeautifulSoup
from requests import RequestException
from concurrent.futures import ThreadPoolExecutor

import logging


class ProxyList:

    def __init__(self):
        self.__proxy_url = "https://www.xicidaili.com/nn/{}"
        self.__check_url = "http://httpbin.org/ip"
        self.__headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70."
                          "0.3538.110 Safari/537.36"
        }
        # 代理列表
        self.__proxy_list = []
        # 原始代理
        self.__init_proxy_list = []
        # 已经使用过的代理
        self.__used_proxy_list = []
        # 无效代理
        self.__bad_proxy_list = []
        # 爬取的页数
        self.__page_num = 1
        # 初始化爬取
        self.__add_proxy_list()

    def __get_html(self, url, proxy=None):
        """
        获取代理网页的源码
        :param url:
        :param proxy:
        :return:
        """
        try:
            r = requests.get(url, headers=self.__headers, proxies=proxy)
            if r.status_code == 200:
                return r.text
        except RequestException as e:
            logging.warning(f"{url} is bad,code,error:{e},proxy：{proxy}")

    def __add_proxy_list(self):
        """
        解析代理并添加代理
        :return:
        """
        url = self.__proxy_url.format(self.__page_num)
        html = self.__get_html(url)
        self.__page_num += 1

        if html:
            soup = BeautifulSoup(html, "lxml")
            proxy_tag_list = soup.select("#ip_list > tr")[1:]
            for proxy_tag in proxy_tag_list:
                ip = proxy_tag.select("td:nth-of-type(2)")[0].get_text().strip()
                port = proxy_tag.select("td:nth-of-type(3)")[0].get_text().strip()
                proxy = {"http": "http://"+ip+":"+port, "https": "http://"+ip+":"+port}
                self.__init_proxy_list.append(proxy)

    def __len__(self):
        return self.__proxy_list

    def __check_proxy(self, proxy):
        """
        检查代理有效性
        :param proxy:
        :return:
        """
        response_ip = self.__get_html(self.__check_url, proxy=proxy)
        if response_ip:
            if proxy["http"] in response_ip:
                return True, proxy
            else:
                return False, proxy
        else:
            return False, proxy

    def check_init_proxy_list(self):
        """
            验证有效性，原始代理分类
            使用多线程加速验证
        """
        with ThreadPoolExecutor(max_workers=8) as pool:
            result_list = pool.map(self.__check_proxy, self.__init_proxy_list)
            for status, result in result_list:
                if status:
                    self.__proxy_list.append(result)
                else:
                    self.__bad_proxy_list.append(result)

    @property
    def get_proxy_list(self):
        """获取代理当前代理列表"""
        return self.__proxy_list

    @property
    def get_proxy(self):
        """获取一个代理"""
        if len(self):
            """当前存在代理"""
            proxy = self.__proxy_list.pop()
            self.__used_proxy_list.append(proxy)
            return proxy
        elif len(self.__used_proxy_list):
            """在用过的代理中找可以用的"""
            for proxy in self.__used_proxy_list:
                self.__used_proxy_list.remove(proxy)
                if self.__check_proxy(proxy):
                    self.__proxy_list.append(proxy)
                    return proxy
                else:
                    self.__bad_proxy_list.append(proxy)
        else:
            """都没有可用的，就再次爬取"""
            self.__add_proxy_list()
            return "当前没有可以用的"

    @property
    def get_bad_proxy_list(self):
        """获取不可用的代理列表"""
        return self.__bad_proxy_list

    @property
    def get_init_proxy_list(self):
        """"获取原始的代理列表"""
        return self.__init_proxy_list


if __name__ == '__main__':
    p = ProxyList()
    print(p.check_init_proxy_list())
    print(p.get_bad_proxy_list)
