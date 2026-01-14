# -*- coding: utf-8 -*-
# @File     : message.py
# @Time     : 2021/10/17 19:24
# @Author   : Jckling

import os
import time
from datetime import datetime, timedelta

import requests

from Bilibili import bilibili_checkin
from Picacomic import pica_checkin
from V2EX import v2ex_checkin
from Yamibo import yamibo_checkin
from Yurifans import yurifans_checkin
from telegram import Bot

# info
TG_USER_ID = os.environ.get("TG_USER_ID")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
SERVERPUSHKEY = os.environ.get("SERVERPUSHKEY")

if __name__ == '__main__':
    start_time = time.time()
    utc_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    content_lst = []

    if os.environ.get("V2EX_COOKIES"):
        content_lst.append(f"「V2EX」\n{v2ex_checkin.main()}")
    if os.environ.get("BILIBILI_COOKIES"):
        content_lst.append(f"「Bilibili」\n{bilibili_checkin.main()}")
    if os.environ.get("YAMIBO_COOKIES"):
        content_lst.append(f"「Yamibo」\n{yamibo_checkin.main()}")
    if os.environ.get("YURIFANS_EMAIL"):
        content_lst.append(f"「Yurifans」\n{yurifans_checkin.main()}")
    if os.environ.get("PICA_EMAIL"):
        content_lst.append(f"「哔咔漫画」\n{pica_checkin.main()}")

    content_lst.append(
        f"开始时间: {utc_time}\n"
        f"任务用时: {int(time.time() - start_time)} 秒\n"
    )
    content = "\n————————————\n\n".join(content_lst)

    if TG_BOT_TOKEN:
        bot = Bot(token=TG_BOT_TOKEN)
        bot.sendMessage(
            chat_id=TG_USER_ID,
            text=content,
            parse_mode="HTML"
        )
    
    if SERVERPUSHKEY:
        server_url = f"https://sctapi.ftqq.com/{SERVERPUSHKEY}.send"
        data = {
            "title": "Daily Bonus 签到通知",
            "desp": content
        }
        try:
            response = requests.post(server_url, data=data)
            if response.status_code == 200:
                print("Server酱推送成功")
            else:
                print(f"Server酱推送失败: {response.status_code}")
        except Exception as e:
            print(f"Server酱推送异常: {str(e)}")

    print(content)
