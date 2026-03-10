import json
import time

import requests

# ========================
# 参数区（经常修改）
# ========================
# token：登录后从请求头里抓到的 token，失效后更新
token = "59420fb74b79d1a449e01d374c757836"

# exam_id：考试实例 id（通常来自 start_exam 返回）
exam_id = 203572

# 考试套题：编号 -> (question_id, right_answer, error_answer)
# 运行考试时输入编号，自动选中对应套题
exam_sets = {
    1: (452, 3, 4),
    2: (436, 2, 3),
    3: (444, 1, 2),
    4: (451, 3, 4),
}

# ========================
# 参数区（不常修改）
# ========================
# 刷课参数
video_id = 368
start_detail_id = 948
end_detail_id = 963
ratio = "100.00"
study_time = 8208.12291393
year = "2026"
study_interval_seconds = 1

# 考试参数
right_count = 35
error_count = 15


def build_common_headers(user_token: str) -> dict:
    """构建通用请求头。"""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.hubei21.com",
        "Referer": "https://www.hubei21.com/",
        "token": user_token,
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0"
        ),
    }


def study_video() -> None:
    """刷课流程：按 detail_id 区间逐条提交。"""
    url = "https://api.hubei21.com/api/video_detail_study"
    headers = build_common_headers(token)
    print(f"开始刷课：detail_id {start_detail_id} -> {end_detail_id}")

    for detail_id in range(start_detail_id, end_detail_id + 1):
        payload = {
            "video_id": video_id,
            "video_detail_id": detail_id,
            "ratio": ratio,
            "time": study_time,
            "year": year,
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"[刷课] detail_id={detail_id} 状态码={resp.status_code} 返回={resp.text}")
        except Exception as exc:
            print(f"[刷课] detail_id={detail_id} 异常={exc}")
        time.sleep(study_interval_seconds)


def build_exam_content_answer(
    question_id: int,
    right_answer: int,
    error_answer: int,
    right_count: int,
    error_count: int,
) -> list:
    """按数量拼装考试答案列表。"""
    content_answer = []
    for _ in range(right_count):
        content_answer.append({"id": question_id, "value": right_answer})
    for _ in range(error_count):
        content_answer.append({"id": question_id, "value": error_answer})
    return content_answer


def choose_exam_set_index() -> int:
    """选择套题编号。"""
    print("可选套题：")
    for idx, (qid, right, error) in exam_sets.items():
        print(f"{idx}) 题目ID={qid} 正确答案={right} 错误答案={error}")

    raw = input("请输入套题编号：").strip()
    try:
        choice = int(raw)
    except ValueError as exc:
        raise ValueError("套题编号必须是整数") from exc

    if choice not in exam_sets:
        raise ValueError("套题编号无效")
    return choice


def print_exam_result(resp: requests.Response) -> None:
    """格式化打印考试结果，有证书链接时单独展示。"""
    print(f"[考试] 状态码={resp.status_code}")

    try:
        body = resp.json()
    except Exception:
        print(f"[考试] 返回={resp.text}")
        return

    code = body.get("code")
    msg = body.get("msg")
    data = body.get("data") if isinstance(body.get("data"), dict) else {}

    print("========== 考试结果 ==========")
    print(f"结果码: {code}    信息: {msg}")
    if data:
        print(f"分数: {data.get('score')}")
        print(f"正确率: {data.get('right_accuracy')}")
        print(f"正确题数: {data.get('right_number')}    错误题数: {data.get('wrong_number')}")
        print(f"用时(秒): {data.get('used_time')}    是否通过: {data.get('pass')}")

        certificate_url = data.get("certificate_url")
        if certificate_url:
            print("--------------------------------")
            print("证书链接:")
            print(certificate_url)
            print("--------------------------------")
    else:
        print("返回中没有 data 详情")
    print("================================")


def submit_exam_once(set_index: int, headers: dict) -> requests.Response:
    """按指定套题提交一次考试。"""
    selected_question_id, selected_right_answer, selected_error_answer = exam_sets[set_index]
    content_answer = build_exam_content_answer(
        question_id=selected_question_id,
        right_answer=selected_right_answer,
        error_answer=selected_error_answer,
        right_count=right_count,
        error_count=error_count,
    )

    payload = {
        "id": exam_id,
        "content_answer": json.dumps(content_answer, ensure_ascii=False),
    }

    print(
        f"[考试] 使用套题 {set_index}：题目ID={selected_question_id} "
        f"正确答案={selected_right_answer} 错误答案={selected_error_answer}"
    )
    return requests.post(
        "https://api.hubei21.com/api/stop_exam",
        headers=headers,
        json=payload,
        timeout=30,
    )


def choose_next_set_after_400(last_set_index: int) -> int:
    """处理 400 后的用户输入：0=重试上次套题，1+ 切换对应套题。"""
    while True:
        raw = input("返回 400：输入 0 重发上次套题，输入 1+ 使用对应套题：").strip()
        try:
            value = int(raw)
        except ValueError:
            print("输入无效，请输入数字。")
            continue

        if value == 0:
            return last_set_index
        if value in exam_sets:
            return value
        print("套题编号不存在，请重新输入。")


def submit_exam() -> None:
    """考试流程：首次选择套题；若返回 400，则按输入重试或切换套题。"""
    headers = build_common_headers(token)
    headers["Accept"] = "application/json"

    current_set_index = choose_exam_set_index()

    while True:
        try:
            resp = submit_exam_once(current_set_index, headers)
        except Exception as exc:
            print(f"[考试] 请求异常={exc}")
            return

        print_exam_result(resp)

        if resp.status_code != 400:
            return

        current_set_index = choose_next_set_after_400(current_set_index)


def main() -> None:
    """程序入口。"""
    print("请选择操作：")
    print("1) 刷课")
    print("2) 考试")
    choice = input("请输入 1 或 2：").strip()

    if choice == "1":
        study_video()
    elif choice == "2":
        submit_exam()
    else:
        print("输入无效。")


if __name__ == "__main__":
    main()
