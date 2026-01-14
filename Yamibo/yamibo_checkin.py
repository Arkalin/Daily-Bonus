# -*- coding: utf-8 -*-
# @File     : yamibo_checkin.py
# @Time     : 2021/04/07 15:48
# @Author   : Jckling

import os

import cloudscraper
from bs4 import BeautifulSoup
from lxml import html

# cookies
COOKIES = os.environ.get("YAMIBO_COOKIES")
msg = []

HEADERS = {
    "Host": "bbs.yamibo.com",
    "Connection": "keep-alive",
    "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-full-version": "123.0.6312.106",
    "sec-ch-ua-arch": "x86",
    "sec-ch-ua-platform": "Windows",
    "sec-ch-ua-platform-version": "15.0.0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-bitness": "64",
    "sec-ch-ua-full-version-list": '"Google Chrome";v="123.0.6312.106", "Not:A-Brand";v="8.0.0.0", "Chromium";v="123.0.6312.106"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://bbs.yamibo.com/plugin.php?id=zqlj_sign",
    # "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8,ja;q=0.7,zh-TW;q=0.6",
    "Cookie": COOKIES,
}

# Bypass Cloudflare
SESSION = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)



# 登录
def fhash():
    url = "https://bbs.yamibo.com/plugin.php?id=zqlj_sign"
    try:
        r = SESSION.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        content = r.text
            
        # 方法1：从表单中提取formhash
        soup = BeautifulSoup(content, 'html.parser')
        formhash_input = soup.find('input', {'name': 'formhash'})
        if formhash_input and formhash_input.get('value'):
            return formhash_input['value']
            
        # 方法2：从搜索表单中提取
        scbar_form = soup.find('form', id='scbar_form')
        if scbar_form:
            formhash_input = scbar_form.find('input', {'name': 'formhash'})
            if formhash_input and formhash_input.get('value'):
                return formhash_input['value']
            
    except Exception as e:
        msg.append({"name": "获取formhash错误", "value": str(e)})
    
    msg.append({"name": "获取formhash失败", "value": "请检查Cookie是否有效"})
    return ""


# 签到
def check_in():
    code = fhash()
    if code == "":
        return False

    url = "https://bbs.yamibo.com/plugin.php?id=zqlj_sign&sign=" + code
    r = SESSION.get(url)
    tree = html.fromstring(r.text)

    global msg
    try:
        message = tree.xpath('//*[@id="messagetext"]/p[1]/text()')[0]
        if "打卡成功" in message:
            msg += [{"name": "签到信息", "value": "签到成功"}]
        elif "打过卡" in message:
            msg += [{"name": "签到信息", "value": "已签到"}]
        elif "登录" in message:
            msg += [{"name": "签到信息", "value": "登录失败，Cookie 可能已失效"}]
            return False
        else:
            msg += [{"name": "签到信息", "value": message}]
            return False
        return True
    except Exception as e:
        msg += [{"name": "check_in error", "value": e}]
        return False


# 查询
def query_credit():
    # 对象信息
    r = SESSION.get("https://bbs.yamibo.com/plugin.php?id=zqlj_sign")
    tree = html.fromstring(r.text)

    global msg
    try:
        checkin_msg = tree.xpath('//div[@class="bm signbtn cl"]/a/text()')[0]
        stat = tree.xpath('//*[@id="wp"]/div[2]/div[2]/div[3]/div[2]/ul/li/text()')
        msg += [{"name": s.split("：")[0], "value": s.split("：")[1]} for s in stat]
    except Exception as e:
        msg += [{"name": "查询对象失败", "value": e}]

    # 积分信息
    r = SESSION.get("https://bbs.yamibo.com/home.php?mod=spacecp&ac=credit")
    soup = BeautifulSoup(r.text, "lxml")
    tree = html.fromstring(str(soup))
    try:
        credit = tree.xpath('//ul[@class="creditl mtm bbda cl"]/li/text()')
        data = [i.strip() for i in credit]
        msg += [
            {"name": "对象", "value": data[1]},
            {"name": "积分", "value": data[2]},
            {"name": "总积分", "value": data[3]},
            {"name": "规则", "value": "总积分 = 积分 + 对象/3"}
        ]
    except Exception as e:
        msg += [{"name": "查询积分失败", "value": e}]


def main():
    SESSION.headers.update(HEADERS)
    if check_in():
        query_credit()
    global msg
    return "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg])


if __name__ == '__main__':
    print(" 300 签到开始 ".center(60, "="))
    print(main())
    print(" 300 签到结束 ".center(60, "="), "\n")
