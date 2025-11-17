"""
Created on 2025/11/17 14:54 
Author: Shuijing
Description: 
"""
import requests
import time

token = "0391c0aa84fd816fff7d048eaacac3ca"
url = "https://api.hubei21.com/api/video_detail_study"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Sec-Fetch-Site": "same-site",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Mode": "cors",
    "Origin": "https://www.hubei21.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15",
    "Referer": "https://www.hubei21.com/",
    "Sec-Fetch-Dest": "empty",
    "Priority": "u=3, i",
    "token": token
}

start_id = 517
end_id = 533   # 你可以改成你要刷的终点 ID

for detail_id in range(start_id, end_id + 1):
    payload = {
        "video_id": 176,             # 固定
        "video_detail_id": detail_id,  # 递增
        "ratio": "100.00",
        "time": 8208.12291393,
        "year": "2025"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers)
        print(f"detail_id={detail_id} 返回状态码: {resp.status_code}")
        print("返回内容:", resp.text)
    except Exception as e:
        print(f"detail_id={detail_id} 请求失败:", e)

    time.sleep(1)  # 间隔 2 秒