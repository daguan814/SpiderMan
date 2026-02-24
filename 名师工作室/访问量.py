import time
from urllib.parse import quote

import requests


INDEX_URL = "https://www.xgjy.cn/studio/index.php?r=studio/post/view&sid=300098&id=52472"
PAGEVIEW_BASE = "https://www.xgjy.cn/studio/index.php?r=studio/pageview&sid=300098&url="
PAGEVIEW_URL_PARAM = quote("r=studio/post/view&sid=300098&id=52472", safe="")
PAGEVIEW_URL = PAGEVIEW_BASE + PAGEVIEW_URL_PARAM

TOTAL = 1000
SLEEP_SECONDS = 0.5
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

    for i in range(1, TOTAL + 1):
        try:
            index_resp = session.get(INDEX_URL, timeout=TIMEOUT_SECONDS)
            index_resp.raise_for_status()

            pageview_resp = session.get(PAGEVIEW_URL, timeout=TIMEOUT_SECONDS)
            pageview_resp.raise_for_status()

            success += 1
            print(
                f"[{i}/{TOTAL}] ok "
                f"index={index_resp.status_code} pageview={pageview_resp.status_code}"
            )
        except Exception as exc:
            failures += 1
            print(f"[{i}/{TOTAL}] fail {exc}")

        if i < TOTAL:
            time.sleep(SLEEP_SECONDS)

    print(f"完成: success={success}, failures={failures}")


if __name__ == "__main__":
    run()
