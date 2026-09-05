import json
from pathlib import Path
import time

import requests

# ========================
# 参数区（经常修改）
# ========================
CONFIG_PATH = Path(__file__).with_name("config.json")

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
exam_retry_wait_seconds = 10 * 60


def load_config() -> dict:
    """读取配置文件。"""
    if not CONFIG_PATH.exists():
        raise ValueError("config.json 不存在。")

    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("config.json 格式错误。") from exc
    except OSError as exc:
        raise ValueError(f"读取 config.json 失败：{exc}") from exc

    if not isinstance(config, dict):
        raise ValueError("config.json 内容必须是对象。")

    return config


def save_config(config: dict) -> None:
    """保存配置文件。"""
    CONFIG_PATH.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def resolve_token(config: dict) -> str:
    """启动时提示输入 token；未输入时使用配置中的 token。"""
    current_token = str(config.get("token", "")).strip()
    raw = input("请输入 token（直接回车则使用 config.json 中的 token）：").strip()
    if raw:
        config["token"] = raw
        save_config(config)
        return raw

    if current_token:
        print("未输入 token，使用 config.json 中的 token。")
        return current_token

    raise ValueError("config.json 中没有可用 token，请先输入 token。")


def resolve_exam_id(config: dict) -> int:
    """考试时提示输入试卷 id；未输入时使用配置中的 id。"""
    current_exam_id = config.get("exam_id")
    raw = input("请输入试卷 id（直接回车则使用 config.json 中的 exam_id）：").strip()

    if raw:
        try:
            exam_id = int(raw)
        except ValueError as exc:
            raise ValueError("试卷 id 必须是整数") from exc
        config["exam_id"] = exam_id
        save_config(config)
        return exam_id

    try:
        exam_id = int(current_exam_id)
    except (TypeError, ValueError) as exc:
        raise ValueError("config.json 中没有有效的 exam_id，请先输入试卷 id。") from exc

    print(f"未输入试卷 id，使用 config.json 中的 exam_id={exam_id}。")
    return exam_id


def normalize_exam_sets(raw_exam_sets: dict) -> dict[int, tuple[int, int, int]]:
    """将配置中的 exam_sets 规范化为 int -> tuple[int, int, int]。"""
    normalized_exam_sets = {}

    if not isinstance(raw_exam_sets, dict):
        raise ValueError("config.json 中的 exam_sets 必须是对象。")

    for raw_key, raw_value in raw_exam_sets.items():
        try:
            set_index = int(raw_key)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"exam_sets 的编号无效：{raw_key}") from exc

        if not isinstance(raw_value, list) or len(raw_value) != 3:
            raise ValueError(
                f"exam_sets[{raw_key}] 必须是长度为 3 的数组：[question_id, right_answer, error_answer]"
            )

        try:
            question_id, right_answer, error_answer = (int(item) for item in raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"exam_sets[{raw_key}] 中的值必须都是整数") from exc

        normalized_exam_sets[set_index] = (
            question_id,
            right_answer,
            error_answer,
        )

    if not normalized_exam_sets:
        raise ValueError("config.json 中的 exam_sets 不能为空。")

    return normalized_exam_sets


def resolve_exam_set_index(config: dict, exam_sets: dict[int, tuple[int, int, int]]) -> int:
    """考试时提示输入套题编号；未输入时使用配置中的编号。"""
    current_exam_set_index = config.get("exam_set_index")
    print("可选套题：")
    for idx, (qid, right, error) in exam_sets.items():
        print(f"{idx}) 题目ID={qid} 正确答案={right} 错误答案={error}")

    raw = input(
        "请输入套题编号（直接回车则使用 config.json 中的 exam_set_index）："
    ).strip()

    if raw:
        try:
            exam_set_index = int(raw)
        except ValueError as exc:
            raise ValueError("套题编号必须是整数") from exc
        if exam_set_index not in exam_sets:
            raise ValueError("套题编号无效")
        config["exam_set_index"] = exam_set_index
        save_config(config)
        return exam_set_index

    try:
        exam_set_index = int(current_exam_set_index)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "config.json 中没有有效的 exam_set_index，请先输入套题编号。"
        ) from exc

    if exam_set_index not in exam_sets:
        raise ValueError("config.json 中的 exam_set_index 不存在于 exam_sets。")

    print(
        f"未输入套题编号，使用 config.json 中的 exam_set_index={exam_set_index}。"
    )
    return exam_set_index


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


def study_video(user_token: str) -> None:
    """刷课流程：按 detail_id 区间逐条提交。"""
    url = "https://api.hubei21.com/api/video_detail_study"
    headers = build_common_headers(user_token)
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
            print(
                f"[刷课] detail_id={detail_id} 状态码={resp.status_code} 返回={resp.text}"
            )
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


def print_exam_result(resp: requests.Response) -> None:
    """格式化打印考试结果，有证书链接时单独展示。"""
    print(f"[考试] 状态码={resp.status_code}")
    print(f"[考试] 完整返回={resp.text}")

    try:
        body = resp.json()
    except Exception:
        return

    if not isinstance(body, dict):
        return

    code = body.get("code")
    msg = body.get("msg")
    data = body.get("data") if isinstance(body.get("data"), dict) else {}

    print("========== 考试结果 ==========")
    print(f"结果码: {code}    信息: {msg}")
    if data:
        print(f"分数: {data.get('score')}")
        print(f"正确率: {data.get('right_accuracy')}")
        print(
            f"正确题数: {data.get('right_number')}    错误题数: {data.get('wrong_number')}"
        )
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


def submit_exam_once(
    set_index: int,
    exam_id: int,
    exam_sets: dict[int, tuple[int, int, int]],
    headers: dict,
) -> requests.Response:
    """按指定套题提交一次考试。"""
    selected_question_id, selected_right_answer, selected_error_answer = exam_sets[
        set_index
    ]
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


def has_passed_exam(resp: requests.Response) -> bool:
    """同时检查 HTTP 状态、业务结果码和通过标记。"""
    if not 200 <= resp.status_code < 300:
        return False
    try:
        body = resp.json()
    except ValueError:
        return False
    if not isinstance(body, dict) or str(body.get("code")) != "200":
        return False
    data = body.get("data")
    return isinstance(data, dict) and data.get("pass") in (1, "1")


def submit_exam(
    user_token: str,
    exam_id: int,
    exam_set_index: int,
    exam_sets: dict[int, tuple[int, int, int]],
) -> None:
    """立即首次提交；未通过则每十分钟重提，通过后自动结束。"""
    headers = build_common_headers(user_token)
    headers["Accept"] = "application/json"

    current_set_index = exam_set_index
    print(f"已选择试卷 id={exam_id}，立即提交。")

    while True:
        try:
            resp = submit_exam_once(current_set_index, exam_id, exam_sets, headers)
        except Exception as exc:
            print(f"[考试] 请求异常={exc}")
        else:
            print_exam_result(resp)
            if has_passed_exam(resp):
                print("考试已通过，程序结束。")
                return

        print("将在 10 分钟后使用当前套题再次提交，按 Ctrl+C 可取消。", flush=True)
        time.sleep(exam_retry_wait_seconds)


def main() -> None:
    """程序入口。"""
    try:
        config = load_config()
        user_token = resolve_token(config)
        exam_sets = normalize_exam_sets(config.get("exam_sets"))
    except ValueError as exc:
        print(exc)
        return

    print("请选择操作：")
    print("1) 刷课")
    print("2) 考试")
    choice = input("请输入 1 或 2：").strip()

    if choice == "1":
        study_video(user_token)
    elif choice == "2":
        try:
            exam_id = resolve_exam_id(config)
            exam_set_index = resolve_exam_set_index(config, exam_sets)
        except ValueError as exc:
            print(exc)
            return
        submit_exam(user_token, exam_id, exam_set_index, exam_sets)
    else:
        print("输入无效。")


if __name__ == "__main__":
    main()
