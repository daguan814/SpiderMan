"""
Created on 2024/12/2 下午8:32 
Author: Shuijing
Description: 
"""
import time

import requests
from http.cookies import SimpleCookie

qi = int(input('请输入您需要刷的期数,3=全部:'))

Cookies = input('请输入您的cookie:')

cookie = SimpleCookie()
cookie.load(Cookies)  #加载cookie
cookie['TheMaxTime'] = '37780' # 修改它的值


cookies = {
    'MaxTimeLength_1977': '0',
    'LocalStudyProgress_1977': 'D00BGwQWVmVeRUVGBjBHQkFRPQtXSEtCTWhQV0VGETZfVUFAFQIFUFNCQ2dURV9XUWcBBgUFCQ%3D%3D',
    'MaxTimeLength_2021': '0',
    'MaxTimeLength_1991': '0',
    'MaxTimeLength_1985': '0',
    'LocalStudyProgress_1985': 'D00BGwQWVmVSREVGBjBHQkFRPQtXSEtCTWdSV0VGETZfVUFAFQIFUFNCQ2dURV9XXGsFBAoDCQ%3D%3D',
    'TheMaxTime': '37780',
    'sl-session': '2+fDD5aySGqs/MC9TDgr5w==',
    '_d_id': 'c6c9034f1fce299a6377f14c478dc8',
    'ASP.NET_SessionId': 'qtppqthsr1uhoksqmd11eviv',
    'SavedLogin': SavedLogin,
}


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://nsstudy.whttc.com',
    'priority': 'u=0, i',
    'referer': 'https://nsstudy.whttc.com/kj/ViewPlay.aspx?xl=1&id=1985',
    'sec-ch-ua': '"Microsoft Edge";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'iframe',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0',
    # 'cookie': 'MaxTimeLength_1977=0; LocalStudyProgress_1977=D00BGwQWVmVeRUVGBjBHQkFRPQtXSEtCTWhQV0VGETZfVUFAFQIFUFNCQ2dURV9XUWcBBgUFCQ%3D%3D; MaxTimeLength_2021=0; MaxTimeLength_1991=0; MaxTimeLength_1985=0; LocalStudyProgress_1985=D00BGwQWVmVSREVGBjBHQkFRPQtXSEtCTWdSV0VGETZfVUFAFQIFUFNCQ2dURV9XXGsFBAoDCQ%3D%3D; TheMaxTime=51; sl-session=2+fDD5aySGqs/MC9TDgr5w==; _d_id=c6c9034f1fce299a6377f14c478dc8; ASP.NET_SessionId=qtppqthsr1uhoksqmd11eviv; SavedLogin=UserName=421126199108057009&Userid=10764',
}


data = {
    '__VIEWSTATE': 'vdC1ojC6F4amKwTO9QDAL8n+lomJwoBqKTT4RQFKOu0Jt1633aifCF9h++kw7QKR3HA8Znpwk0Gd0LA7ulggbWazDf9NeF7tA/mlWtm5YEd8fLEBKVREJ/ipgDZqoOsHby2EBw==',
    '__VIEWSTATEGENERATOR': '5620F3FD',
    '__EVENTVALIDATION': 'A/UUYPmXJhZ84GZcSMyG2+Krf+F/Zlu0Vw/63aiFKN5wPF06v4gmKx8zaQ3dPBtGJ0tsoDr8mH2QwbbhFiAL2ipVR1PP5rpJSB8uWjyEO+LuNeuHL4kPVzZov1zjgPK71Nb77eJT9H5bDIgvyGWOmBWudrc=',
    'Button1': 'Button',
}


def shuake(x, y):
    for i in range(x, y):
        params = {
            'xl': '1',
            'id': i,
        }
        response = requests.post(
            'https://nsstudy.whttc.com/kj/ViewPlay.aspx',
            params=params,
            cookies=cookies,
            headers=headers,
            data=data,
            verify=False,
        )
        print(response.text, i)
        time.sleep(1)


if qi == 1:
    shuake(1977, 2022)    # 这里填写刷课的期数区间
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
