from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


URL = "https://www.xgjy.cn/studio/index.php?r=studio/post/view&sid=300098&id=53990"


def main():
    req = Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
        method="GET",
    )

    try:
        with urlopen(req, timeout=10) as resp:
            status = getattr(resp, "status", resp.getcode())
            body = resp.read(500).decode("utf-8", errors="replace")
            print("status:", status)
            print("body_preview:")
            print(body)
    except HTTPError as e:
        print("http_error:", e.code, e.reason)
    except URLError as e:
        print("url_error:", e.reason)
    except Exception as e:
        print("error:", repr(e))


if __name__ == "__main__":
    main()
