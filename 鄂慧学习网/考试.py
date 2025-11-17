"""
Created on 2025/11/17 15:05 
Author: Shuijing
Description: 
"""
import requests
import json

# -------------------------
# 定义 token 和 id
# -------------------------
token = "0391c0aa84fd816fff7d048eaacac3ca"
exam_id = 195054
question_id = 379
answer = 2

# 答案库
'''
试题id: 379, 
  答案: 2  , 
'''

url = "https://api.hubei21.com/api/stop_exam"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "token": token
}

# -------------------------
# 拼接 content_answer 的列表
# -------------------------
content_answer = []

# 加 35 个 id=379,value=2
for _ in range(35):
    content_answer.append({"id": question_id, "value": answer})

# 加 15 个 id=3,value=你要的值
for _ in range(15):
    content_answer.append({"id": question_id, "value": answer + 1})  # 自己填数值

# -------------------------
# 整个 payload（只发一次请求）
# -------------------------
payload = {
    "id": exam_id,
    "content_answer": json.dumps(content_answer, ensure_ascii=False)
}

resp = requests.post(url, headers=headers, json=payload)

print("状态:", resp.status_code)
print("返回:", resp.text)
