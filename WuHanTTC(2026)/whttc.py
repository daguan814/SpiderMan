"""
Created on 2024/12/2 下午8:32
Author: Shuijing
Description: 武汉导游年审（nsstudy.whttc.com）自动刷课脚本

原脚本为什么跑不通：
1. `SavedLogin = SavedLogin` 引用了没定义的变量，一运行就 NameError；
2. __VIEWSTATE / __EVENTVALIDATION 被写死在代码里。ASP.NET 会校验这两个字段的签名，
   拿旧的（或别的会话的）值去 POST，服务器直接返回 500「运行时错误」；
3. referer 固定成某一节课（id=1985），和当前刷的课程对不上。

修复思路：每节课先 GET 一次页面，从返回的 HTML 里取本次会话有效的隐藏字段，
再带着它们 POST 触发 Button1；cookie 直接解析用户粘贴进来的那串。
"""

import re
import time
import warnings

import requests
from http.cookies import SimpleCookie

# verify=False 会触发 InsecureRequestWarning，这里统一屏蔽掉
warnings.filterwarnings('ignore')

BASE_URL = 'https://nsstudy.whttc.com/kj/ViewPlay.aspx'
MAX_TIME = '37780'  # 写进 cookie 的 TheMaxTime

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'origin': 'https://nsstudy.whttc.com',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Microsoft Edge";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'iframe',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0',
}

# POST 时必须带上的三个 ASP.NET 隐藏字段
HIDDEN_FIELDS = ('__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION')


def parse_cookies(raw: str) -> dict:
    """把浏览器里复制出来的 cookie 字符串解析成字典，并补上 TheMaxTime。"""
    cookie = SimpleCookie()
    cookie.load(raw)
    jar = {key: morsel.value for key, morsel in cookie.items()}
    jar['TheMaxTime'] = MAX_TIME
    return jar


def get_hidden_fields(session: requests.Session, course_url: str) -> dict:
    """先 GET 一次课程页，从 HTML 里取出本次会话有效的隐藏字段。"""
    resp = session.get(course_url, headers={**HEADERS, 'referer': course_url}, verify=False, timeout=15)
    resp.encoding = 'utf-8'
    fields = {}
    for name in HIDDEN_FIELDS:
        match = re.search(r'id="%s"[^>]*value="([^"]*)"' % name, resp.text)
        if match:
            fields[name] = match.group(1)
    return fields


def shuake(x: int, y: int, session: requests.Session) -> None:
    """刷 [x, y) 区间的课程。"""
    for i in range(x, y):
        course_url = f'{BASE_URL}?xl=1&id={i}'
        try:
            data = get_hidden_fields(session, course_url)
            if '__VIEWSTATE' not in data:
                print(f'[{i}] 没取到 __VIEWSTATE，可能登录已失效，已跳过')
                continue

            data['Button1'] = 'Button'
            resp = session.post(
                BASE_URL,
                params={'xl': '1', 'id': i},
                headers={**HEADERS, 'referer': course_url,
                         'content-type': 'application/x-www-form-urlencoded'},
                data=data,
                verify=False,
                timeout=15,
            )
            finished = '播放已完成' in resp.text
            print(f'[{i}] HTTP {resp.status_code} {"播放已完成" if finished else "未完成"}')
        except requests.RequestException as exc:
            print(f'[{i}] 请求出错：{exc}')
        time.sleep(2)  # 间隔时间


'''
在这里修改即可。
'''


def main() -> None:
    qi = int(input('请输入您需要刷的期数,3=全部:'))
    cookies = parse_cookies(input('请输入您的cookie:'))

    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(cookies)

    if qi == 1:
        shuake(1977, 2022, session)  # 这里填写刷课的期数区间
        print('刷完1期')
    elif qi == 2:
        shuake(2023, 2067, session)
        print('刷完2期')
    elif qi == 3:
        shuake(796, 858, session)
        print('刷完1期')
        shuake(2023, 2067, session)
        print('刷完2期')
        print('全部刷完')
    else:
        print('期数只能填 1 / 2 / 3')


if __name__ == '__main__':
    main()
