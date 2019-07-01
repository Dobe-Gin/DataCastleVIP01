"""
homework：第一次第三个
python version: 3.7+
author: 小菜鸟
date：20190701

"""
import asyncio
import aiohttp
import json
import hashlib
import time


async def get_response(url, params):
    """
    :param url: 请求的url
    :param params: url中参数
    :return: response.text()

    """
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(url, params=params) as response:
            return await response.text()

async def get_contents(music_id, nums):
    """
    :param music_id: 歌曲id
    :param nums: 爬去的评论的页数
    :return: 歌曲的评论列表，非热评

    """

    contents = []
    url = "https://api.imjad.cn/cloudmusic/"
    params = [{"type": "comments", "id": str(music_id), "offset": str(num)} for num in range(1, nums)]
    tasks = [asyncio.create_task(get_response(url, param)) for param in params]
    responses = await asyncio.gather(*tasks)
    for response in responses:
        response = json.loads(response)
        for content in response["comments"]:
            contents.append(content["content"])
    return contents


async def zh_to_en(content, appid, pwd):
    """

    :param content: 要翻译的歌曲评论
    :param appid: 百度翻译api的appid
    :param pwd: 百度翻译api的密钥
    :return: 中转英的结果

    """

    q = content
    salt = int(time.time())
    sign = str(appid) + q + str(salt) + pwd

    url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
    params = {
        "q": q,
        "salt": salt,
        "appid": appid,
        "from": "zh",
        "to": "en",
        "sign": hashlib.md5(sign.encode(encoding='UTF-8')).hexdigest(),
    }

    result = await asyncio.create_task(get_response(url, params))
    return json.loads(result)["trans_result"][0]["dst"] if "trans_result" in result else "Translate fail"


async def main():
    """

    :return: None，生成翻译后的文件
    注意：替换自己的appid和pwd

    """
    contents = await get_contents(569213220, nums=10)
    tasks = [asyncio.create_task(zh_to_en(content, 2015063000000001, "12345678")) for content in contents]
    results = await asyncio.gather(*tasks)
    with open("result.txt", "a+", encoding="utf-8") as f:
        for result in results:
            f.write(f"{result}" + "\n")


if __name__ == '__main__':
    asyncio.run(main())
