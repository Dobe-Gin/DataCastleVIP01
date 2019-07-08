import requests
from requests.exceptions import RequestException
from urllib import parse
from bs4 import BeautifulSoup
import time
import random
import pandas
import functools

bad_urls = []


def get_urls(pages, kw="zh"):
    """
    :param pages: 爬取的页数
    :param kw: 城市代码，默认zh
    :return: 返回url list
    """
    url = "https://{city}.lianjia.com/zufang/pg{pg_num}/#contentList"
    urls = [url.format(pg_num=page, city=parse.quote(kw, 'utf-8')) for page in range(1, pages + 1)]
    return urls


def get_html(url):
    """
    :param url: 爬取的url
    :return: 返回响应内容
    """
    time.sleep(random.randint(0, 15))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.text
    except RequestException as e:
        print(f"{url} is bad,code:{r.status_code},error:{e}")
        bad_urls.append(url)


def supplement_list(l, l_len):
    """
    因为内容长度不一，需要补长统一
    :param l: 要补长的list
    :param l_len: 目标长度
    :return: 返回补长后的list
    """
    new_l = list(l)
    while len(new_l) < l_len:
        new_l.insert(0, "None")
    return new_l


def analytic_html(html):
    """
    title_list:标题列表
    price_list:价格列表
    addr_list:地址列表
    area_list:面值列表
    direction_list:朝向列表
    shape_list:房型列表
    解析响应内容
    :param html:要解析的html
    :return: 返回解析后的内容
    """
    # 各字段的list
    title_list = []
    price_list = []
    addr_list = []
    area_list = []
    direction_list = []
    shape_list = []

    soup = BeautifulSoup(html, "lxml")
    contents = soup.find_all("div", class_="content__list--item--main")

    for content in contents:
        other_list = content.select(".content__list--item--des")[0].get_text().split("/")
        title_list.append(content.select(".content__list--item--title > a")[0].get_text().strip())
        price_list.append(content.select(".content__list--item-price > em")[0].get_text())

        # 补长list
        new_other_list = supplement_list(other_list, 4)

        # 第一个不是地址就为None
        if "-" not in new_other_list[0]:
            new_other_list[0] = "None"

        # 添加各字段内容到list
        addr_list.append(new_other_list[0].strip())
        area_list.append(new_other_list[1].strip())
        direction_list.append(new_other_list[2].strip())
        shape_list.append(new_other_list[3].strip())

    return title_list, addr_list, area_list, direction_list, shape_list, price_list


def write_csv(func):
    """
    写入csv的装饰器，装饰主调用函数
    :param func: 传入的函数
    :return:
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("写入csv")
        contents = list(func(*args, **kwargs))
        df = pandas.DataFrame(contents[0])
        df.to_csv("lianjia.csv", encoding="utf-8-sig")
        print(df)
        print("写入完毕")

    return wrapper


@write_csv
def main():
    """
    主调用函数，整合各个函数内容
    :return: 生成器
    """
    title_list = []
    addr_list = []
    area_list = []
    direction_list = []
    shape_list = []
    price_list = []

    # 获取html list，可自行传入页数
    html_list = [get_html(url) for url in get_urls(2)]

    for html in html_list:
        if html:
            title, addr, area, direction, shape, price = analytic_html(html)
            title_list.extend(title)
            addr_list.extend(addr)
            area_list.extend(area)
            direction_list.extend(direction)
            shape_list.extend(shape)
            price_list.extend(price)

    yield {
        "title": title_list,
        "addr": addr_list,
        "area": area_list,
        "direction": direction_list,
        "shape": shape_list,
        "price": price_list,
    }


if __name__ == '__main__':
    main()
