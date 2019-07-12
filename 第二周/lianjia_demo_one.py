import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import time
import random
import pandas
import functools
import logging

bad_urls = []


def get_proxy():
    """
        因为免费的爬取下来，验证时基本都是不可以用的代理
        因此在这里使用阿布云的代理
        但是7-12过期了，可以自行注册替换
    """
    # 代理服务器
    proxy_host = "http-pro.abuyun.com"
    proxy_port = "9010"

    # 代理隧道验证信息
    proxy_user = "H2O68H0VI19F6G5P"
    proxy_pass = "5364885539DF4294"

    proxy_meta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxy_host,
        "port": proxy_port,
        "user": proxy_user,
        "pass": proxy_pass,
    }

    return {"http": proxy_meta, "https": proxy_meta, }


def get_urls(pages, kw="zh"):
    """
    :param pages: 爬取的页数
    :param kw: 城市代码，默认zh
    :return: 返回url list
    """
    url = "https://{city}.lianjia.com/zufang/pg{pg_num}/#contentList"
    urls = [url.format(pg_num=page, city=kw) for page in range(1, pages + 1)]
    return urls


def get_html(url, proxy=None):
    """
    :param proxy: 代理，默认不使用
    :param url: 爬取的url
    :return: 返回响应内容
    """
    # 10s内随机sleep
    time.sleep(random.randint(0, 11))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.353"
                      "8.110 Safari/537.36"
    }
    try:
        if proxy:
            print(f"get_html的proxy:{proxy}")
        r = requests.get(url, headers=headers, proxies=proxy)
        if r.status_code == 200:
            print(f"请求链接：{url} ......ok")
            return r.text
    except RequestException as e:
        logging.warning(f"{url} is bad,code:{r.status_code},error:{e}")
        bad_urls.append(url)


def analytic_room_html(html):
    """
    解析响应内容
    :param html:要解析的html
    :return: content_list 返回包含解析后的字段list
    """

    content_list = []
    soup = BeautifulSoup(html, "lxml")
    contents = soup.find_all("div", class_="content__list--item--main")

    for content in contents:
        # other_tag：包含地区、大小、朝向、房型的标签
        other_tag = content.select(".content__list--item--des")[0]
        # 判断other_tag是否包含a标签，a标签的内容是地区，剔除脏数据
        if other_tag.find("a"):
            # other_list：包含地区、大小、朝向、房型的文本内容
            other_list = [other.strip() for other in other_tag.get_text().split("/")][:4]
            # 标题
            title = content.select(".content__list--item--title > a")[0].get_text().strip()
            # 价格
            price = content.select(".content__list--item-price > em")[0].get_text()
            # 组合各字段数据
            content_list.append([title, *other_list, price])

    return content_list


def write_csv(file_name="room1.csv"):
    """
    写入csv的装饰器，如果想要写入csv直接加到main()即可"
    :param file_name: 保存的文件，默认为room，csv
    :return: None
    """
    def write_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print("写入csv......")
            contents = list(func(*args, **kwargs))
            df = pandas.DataFrame(contents, columns=["标题", "地区", "大小", "朝向", "房型", "价格"])
            df.to_csv(file_name, encoding="utf-8-sig")
            print(df.head(5))
            print("写入完毕......")
        return wrapper
    return write_decorator


@write_csv()
def main():
    """
    主调用函数，整合各个函数内容
    :return: content_list,内容数组
    """
    content_list = []
    # 获取代理
    proxy = get_proxy()
    html_list = [get_html(url, proxy) for url in get_urls(92)]

    for html in html_list:
        if html:
            content_list.extend(analytic_room_html(html))

    return content_list


if __name__ == '__main__':
    main()

