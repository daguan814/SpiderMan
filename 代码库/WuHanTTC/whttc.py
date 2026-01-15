"""
Created on 2024/12/2 下午8:32 
Author: Shuijing
Description: 
"""
import time

import requests

qi = int(input('请输入您需要刷的期数,3=全部:'))
cookie = input('请输入您的cookie:')
cookies = {
    'TheMaxTime': '34245.23',
    'ASP.NET_SessionId': 'mk3gwpfi2x0yj1egvcnrrlx5',
    'SavedLogin': cookie,
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Content-Type': 'application/x-www-form-urlencoded',
    # 'Cookie': 'TheMaxTime=0; ASP.NET_SessionId=mk3gwpfi2x0yj1egvcnrrlx5; SavedLogin=UserName=429005199509180024&Userid=12138',
    'Origin': 'http://nsstudy.whttc.com',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://nsstudy.whttc.com/kj/ViewPlay.aspx?xl=1&id=796',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}
data = {
    '__VIEWSTATE': 'sqFQuzhTgeiq+qvz2qk66fwZnlMxQCff6309dm70XoOryZGbW75GWX5e1laQRfPztiBEX0s1CSL88XDp+vHXSA30UHxjonT0+CF9xO6LwTGosP0g7DJbZWdiIhOOZf+c2M/YXw==',
    '__VIEWSTATEGENERATOR': '5620F3FD',
    '__EVENTVALIDATION': 'BzGJXrBm+EMed7yV/KCXd5xeKhp01PQHuW++IhQTjzixigieagOSnHVmpdo9MgLAUULN8yXr9LYLfxNkqs6/At1HmFE6SKqUaWOLHREiI9GIDkFbeUUMgEuqrEejfADYk7Ml3ZsNQAza6BglvdAbbnGppW0=',
    'Button1': 'Button',
}


def shuake(x, y):
    for i in range(x, y):
        params = {
            'xl': '1',
            'id': i,
        }
        response = requests.post(
            'http://nsstudy.whttc.com/kj/ViewPlay.aspx',
            params=params,
            cookies=cookies,
            headers=headers,
            data=data,
            verify=False,
        )
        print(response.text, i)
        time.sleep(1)


if qi == 1:
    shuake(796, 858)
    print('刷完1期')

if qi == 2:
    shuake(859, 909)
    print('刷完2期')

if qi == 3:
    shuake(796, 858)
    print('刷完1期')
    shuake(859, 909)
    print('刷完2期')
    print('全部刷完')