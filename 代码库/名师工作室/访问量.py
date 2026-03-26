import random
import time
from urllib.parse import quote

import requests


INDEX_URL = "https://www.xgjy.cn/studio/index.php?r=studio/index/index&sid=300098"
PAGEVIEW_BASE = "https://www.xgjy.cn/studio/index.php?r=studio/pageview&sid=300098&url="
PAGEVIEW_URL_PARAM = quote("r=studio/index/index&sid=300098", safe="")
PAGEVIEW_URL = PAGEVIEW_BASE + PAGEVIEW_URL_PARAM

TOTAL = 1000
INTERVAL_MIN_SECONDS = 0.08
INTERVAL_MAX_SECONDS = 0.25
FAIL_BACKOFF_MIN_SECONDS = 0.5
FAIL_BACKOFF_MAX_SECONDS = 1.2
TIMEOUT_SECONDS = 15


def run() -> None:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }
    )

    success = 0
    failures = 0
    consecutive_failures = 0

    for i in range(1, TOTAL + 1):
        try:
            index_resp = session.get(INDEX_URL, timeout=TIMEOUT_SECONDS)
            index_resp.raise_for_status()

            pageview_resp = session.get(PAGEVIEW_URL, timeout=TIMEOUT_SECONDS)
            pageview_resp.raise_for_status()

            success += 1
            consecutive_failures = 0
            print(
                f"[{i}/{TOTAL}] ok "
                f"index={index_resp.status_code} pageview={pageview_resp.status_code}"
            )
        except Exception as exc:
            failures += 1
            consecutive_failures += 1
            print(f"[{i}/{TOTAL}] fail {exc}")

        if i < TOTAL:
            if consecutive_failures >= 2:
                sleep_seconds = random.uniform(
                    FAIL_BACKOFF_MIN_SECONDS, FAIL_BACKOFF_MAX_SECONDS
                )
            else:
                sleep_seconds = random.uniform(
                    INTERVAL_MIN_SECONDS, INTERVAL_MAX_SECONDS
                )
            time.sleep(sleep_seconds)

    print(f"完成: success={success}, failures={failures}")


if __name__ == "__main__":
    run()
