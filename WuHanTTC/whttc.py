"""
Created on 2024/12/2 下午8:32 
Author: Shuijing
Description: 武汉TTT学习平台刷课工具
"""
import time

import requests

qi = int(input('请输入您需要刷的期数,3=全部:'))
cookie = str(input('请输入您的cookie,仅需要:SavedLogin:'))

# 从curl命令中提取的更新后的请求头
cookies = {'MaxTimeLength_932': '0', 'TheMaxTime': '0', 'MaxTimeLength_967': '0', 'MaxTimeLength_917': '0',
           'MaxTimeLength_1976': '0',
           'LocalStudyProgress_1918': 'D00BGwQWVmVTTVlIRzxdRUBHESYRUFNRRWZWTUtIRytbXVdHAA4YAktJRWhSQl9XXGoKAwIHQxI%3D',
           'MaxTimeLength_1918': '0', 'ASP.NET_SessionId': 'w3nv1w3r3tuoiyaz4eubsctc', 'SavedLogin': cookie}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    # 'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
    'Origin': 'http://nsstudy.whttc.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Safari/605.1.15',
    'Referer': 'http://nsstudy.whttc.com/kj/ViewPlay.aspx?xl=1&id=932',
    'Upgrade-Insecure-Requests': '1',
    # 'Content-Length': '394',
    'Connection': 'keep-alive',
    # 'Cookie': 'MaxTimeLength_932=0; TheMaxTime=0; MaxTimeLength_967=0; MaxTimeLength_917=0; MaxTimeLength_1976=0; LocalStudyProgress_1918=D00BGwQWVmVTTVlIRzxdRUBHESYRUFNRRWZWTUtIRytbXVdHAA4YAktJRWhSQl9XXGoKAwIHQxI%3D; MaxTimeLength_1918=0; ASP.NET_SessionId=w3nv1w3r3tuoiyaz4eubsctc; SavedLogin=UserName=421126199108057009&Userid=10764',
    'Priority': 'u=0, i',
}

data = {
    '__VIEWSTATE': 'waWLDjUJQ5rDNN080R+Mo08AjJVxiqaEgdf4Mw+39zv4xzE2HGQiwhObvEjXCs4YY5bW72bBC+QzF4I94wMmGUOYaFpR4oT/FqO9mTPUysVQ9AlknemUh9aCy0kTasL5US8IyA==',
    '__VIEWSTATEGENERATOR': '5620F3FD',
    '__EVENTVALIDATION': 'TQq4lj3nsmCoZ076HkwzZs/jsO+AZ28OR482dFtwFUCh9vLegHBzp2vYvL/FNZuqQq1bSYXC0efQsbGx3V/+PUyPS0x4ejeEv+oaTGffIk4Z2so0JeVWIo9C1mLkjOB4n6EnecPcjVPKHCw49WqGq7dxRtY=',
    'Button1': 'Button',
}


def shuake(start, end):
    """刷课函数，接受起始和结束id"""
    for i in range(start, end + 1):
        params = {
            'xl': '1',
            'id': start,
        }
        response = requests.post('http://nsstudy.whttc.com/kj/ViewPlay.aspx', params=params, cookies=cookies,
                                 headers=headers,
                                 data=data)
        print(response.text)
        time.sleep(1.5)


if qi == 1:
    # 更新为新的课程ID范围
    shuake(917, 967)  # 假设新课程范围，可以根据实际情况调整
    print('刷完2期')

if qi == 2:
    shuake(1918, 1976)
    print('刷完1期')

if qi == 3:
    shuake(1918, 1976)
    print('刷完1期')
    shuake(917, 967)  # 更新为新课程范围
    print('刷完2期')
    print('全部刷完')