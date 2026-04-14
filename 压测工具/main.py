from __future__ import annotations

import json
import os
import threading
import time
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs
from urllib.request import Request, urlopen


INDEX_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>压测工具</title>
  <style>
    :root {
      --bg: #0f172a;
      --panel: #111827;
      --panel-2: #1f2937;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --accent: #38bdf8;
      --accent-2: #22c55e;
      --danger: #ef4444;
      --border: #334155;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
        "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(56, 189, 248, 0.16), transparent 30%),
        radial-gradient(circle at top right, rgba(34, 197, 94, 0.12), transparent 28%),
        var(--bg);
      min-height: 100vh;
      padding: 32px;
    }
    .wrap {
      max-width: 1080px;
      margin: 0 auto;
    }
    .hero {
      margin-bottom: 20px;
    }
    .hero h1 {
      margin: 0 0 8px;
      font-size: 30px;
      letter-spacing: 0.02em;
    }
    .hero p {
      margin: 0;
      color: var(--muted);
    }
    .grid {
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 18px;
    }
    .card {
      background: rgba(17, 24, 39, 0.92);
      border: 1px solid rgba(51, 65, 85, 0.8);
      border-radius: 16px;
      box-shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
      overflow: hidden;
    }
    .card h2 {
      margin: 0;
      padding: 16px 18px;
      border-bottom: 1px solid var(--border);
      font-size: 16px;
    }
    .body {
      padding: 18px;
    }
    label {
      display: block;
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 6px;
    }
    input {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: var(--panel-2);
      color: var(--text);
      padding: 12px 12px;
      font-size: 14px;
      outline: none;
    }
    input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
    }
    .field { margin-bottom: 14px; }
    .buttons {
      display: flex;
      gap: 10px;
      margin-top: 6px;
    }
    button {
      border: 0;
      border-radius: 10px;
      padding: 11px 14px;
      font-weight: 600;
      cursor: pointer;
      color: white;
      transition: transform 0.08s ease, opacity 0.2s ease;
    }
    button:hover { opacity: 0.95; }
    button:active { transform: translateY(1px); }
    .primary { background: linear-gradient(135deg, var(--accent), #0ea5e9); }
    .secondary { background: linear-gradient(135deg, var(--accent-2), #16a34a); }
    .danger { background: linear-gradient(135deg, var(--danger), #dc2626); }
    .status {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 12px;
      color: var(--muted);
      font-size: 13px;
    }
    .pill {
      padding: 6px 10px;
      border-radius: 999px;
      background: rgba(51, 65, 85, 0.6);
      border: 1px solid rgba(71, 85, 105, 0.7);
    }
    .log {
      height: 560px;
      overflow: auto;
      background: rgba(2, 6, 23, 0.45);
      border-top: 1px solid var(--border);
      padding: 16px 18px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
        "Liberation Mono", monospace;
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.5;
      font-size: 13px;
    }
    .hint {
      margin-top: 12px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.6;
    }
    .error {
      color: #fecaca;
    }
    @media (max-width: 900px) {
      body { padding: 18px; }
      .grid { grid-template-columns: 1fr; }
      .log { height: 420px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <h1>压测工具</h1>
      <p>输入网址、压测次数和压测间隔后即可开始。请求方式为 GET。</p>
    </div>

    <div class="grid">
      <div class="card">
        <h2>参数</h2>
        <div class="body">
          <div class="field">
            <label for="url">网址</label>
            <input id="url" placeholder="https://example.com" />
          </div>
          <div class="field">
            <label for="count">压测次数</label>
            <input id="count" type="number" min="1" step="1" value="10" />
          </div>
          <div class="field">
            <label for="interval">压测间隔（秒）</label>
            <input id="interval" type="number" min="0" step="0.1" value="1" />
          </div>
          <div class="buttons">
            <button class="primary" id="startBtn" onclick="startTest()">开始压测</button>
            <button class="danger" id="stopBtn" onclick="stopTest()">停止</button>
          </div>
          <div class="hint">
            说明：请只对你有权限测试的目标使用。页面会实时刷新日志和状态。
          </div>
        </div>
      </div>

      <div class="card">
        <h2>运行状态</h2>
        <div class="body">
          <div class="status">
            <span class="pill" id="statePill">状态：未知</span>
            <span class="pill" id="progressPill">进度：-</span>
            <span class="pill" id="resultPill">结果：-</span>
          </div>
        </div>
        <div class="log" id="log"></div>
      </div>
    </div>
  </div>

  <script>
    async function api(path, payload) {
      const res = await fetch(path, {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: new URLSearchParams(payload)
      });
      return await res.json();
    }

    function setText(id, text) {
      document.getElementById(id).textContent = text;
    }

    function renderState(data) {
      setText("statePill", "状态：" + data.status);
      setText("progressPill", "进度：" + data.progress);
      setText("resultPill", "结果：成功 " + data.success + " / 失败 " + data.failure);
      document.getElementById("log").textContent = data.logs.join("\\n");
      const log = document.getElementById("log");
      log.scrollTop = log.scrollHeight;
      document.getElementById("startBtn").disabled = data.running;
      document.getElementById("stopBtn").disabled = !data.running;
    }

    async function refresh() {
      const res = await fetch("/state");
      const data = await res.json();
      renderState(data);
    }

    async function startTest() {
      const payload = {
        url: document.getElementById("url").value,
        count: document.getElementById("count").value,
        interval: document.getElementById("interval").value,
      };
      const data = await api("/start", payload);
      if (!data.ok) {
        alert(data.error);
      }
      await refresh();
    }

    async function stopTest() {
      await api("/stop", {});
      await refresh();
    }

    window.addEventListener("load", async () => {
      await refresh();
      setInterval(refresh, 1000);
    });
  </script>
</body>
</html>
"""


class LoadTestState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.running = False
        self.status = "等待开始"
        self.url = ""
        self.count = 0
        self.interval = 0.0
        self.success = 0
        self.failure = 0
        self.current = 0
        self.total = 0
        self.logs: list[str] = []
        self.stop_event = threading.Event()
        self.worker_thread: threading.Thread | None = None

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            progress = f"{self.current}/{self.total}" if self.total else "-"
            return {
                "running": self.running,
                "status": self.status,
                "progress": progress,
                "success": self.success,
                "failure": self.failure,
                "logs": list(self.logs),
            }

    def append_log(self, message: str) -> None:
        with self.lock:
            stamp = time.strftime("%H:%M:%S")
            self.logs.append(f"[{stamp}] {message}")
            if len(self.logs) > 300:
                self.logs = self.logs[-300:]

    def reset_for_run(self, url: str, count: int, interval: float) -> None:
        with self.lock:
            self.running = True
            self.status = "正在启动"
            self.url = url
            self.count = count
            self.interval = interval
            self.success = 0
            self.failure = 0
            self.current = 0
            self.total = count
            self.logs = []
            self.stop_event.clear()

    def finish(self, status: str) -> None:
        with self.lock:
            self.running = False
            self.status = status


class LoadTester:
    def __init__(self, state: LoadTestState) -> None:
        self.state = state

    def start(self, url: str, count: int, interval: float) -> None:
        with self.state.lock:
            if self.state.running:
                raise RuntimeError("压测正在进行中")

        self.state.reset_for_run(url, count, interval)
        self.state.append_log(
            f"开始压测：url={url} 次数={count} 间隔={interval} 秒"
        )

        worker = threading.Thread(
            target=self._run,
            args=(url, count, interval),
            daemon=True,
        )
        with self.state.lock:
            self.state.worker_thread = worker
        worker.start()

    def stop(self) -> None:
        self.state.stop_event.set()
        self.state.append_log("收到停止请求，当前请求完成后将结束。")
        with self.state.lock:
            if self.state.running:
                self.state.status = "正在停止"

    def _run(self, url: str, count: int, interval: float) -> None:
        success = 0
        failure = 0

        for index in range(1, count + 1):
            if self.state.stop_event.is_set():
                self.state.append_log("压测已停止。")
                self.state.finish("已停止")
                return

            with self.state.lock:
                self.state.current = index
                self.state.status = "运行中"

            start_time = time.perf_counter()
            try:
                req = Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    method="GET",
                )
                with urlopen(req, timeout=30) as resp:
                    status = getattr(resp, "status", resp.getcode())
                    body_preview = resp.read(120).decode("utf-8", errors="replace")
                elapsed = time.perf_counter() - start_time
                success += 1
                self.state.append_log(
                    f"[{index}/{count}] 成功 status={status} 耗时={elapsed:.3f}s 预览={body_preview[:60]}"
                )
            except HTTPError as exc:
                elapsed = time.perf_counter() - start_time
                failure += 1
                self.state.append_log(
                    f"[{index}/{count}] HTTP错误 code={exc.code} reason={exc.reason} 耗时={elapsed:.3f}s"
                )
            except URLError as exc:
                elapsed = time.perf_counter() - start_time
                failure += 1
                self.state.append_log(
                    f"[{index}/{count}] 网络错误 reason={exc.reason} 耗时={elapsed:.3f}s"
                )
            except Exception as exc:
                elapsed = time.perf_counter() - start_time
                failure += 1
                self.state.append_log(
                    f"[{index}/{count}] 其他错误 {exc!r} 耗时={elapsed:.3f}s"
                )

            with self.state.lock:
                self.state.success = success
                self.state.failure = failure

            if index < count and not self.state.stop_event.is_set() and interval > 0:
                remaining = interval
                while remaining > 0 and not self.state.stop_event.is_set():
                    sleep_step = min(0.1, remaining)
                    time.sleep(sleep_step)
                    remaining -= sleep_step

        self.state.append_log(f"压测结束，成功 {success} 次，失败 {failure} 次。")
        self.state.finish("压测完成")


class RequestHandler(BaseHTTPRequestHandler):
    state: LoadTestState
    tester: LoadTester
    server_version = "LoadTestGUI/1.0"

    def _send_json(self, data: dict[str, Any], status: int = 200) -> None:
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _send_html(self) -> None:
        payload = INDEX_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _read_form(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        parsed = parse_qs(raw, keep_blank_values=True)
        return {key: values[0] if values else "" for key, values in parsed.items()}

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/" or self.path.startswith("/?"):
            self._send_html()
            return
        if self.path == "/state":
            self._send_json(self.state.snapshot())
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_HEAD(self) -> None:  # noqa: N802
        if self.path == "/" or self.path.startswith("/?"):
            payload = INDEX_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        if self.path == "/state":
            payload = json.dumps(self.state.snapshot(), ensure_ascii=False).encode(
                "utf-8"
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/start":
            self._handle_start()
            return
        if self.path == "/stop":
            self.tester.stop()
            self._send_json({"ok": True, "state": self.state.snapshot()})
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def _handle_start(self) -> None:
        form = self._read_form()
        try:
            url = form.get("url", "").strip()
            if not url:
                raise ValueError("请输入网址")

            try:
                count = int(form.get("count", "").strip())
            except ValueError as exc:
                raise ValueError("压测次数必须是整数") from exc
            if count <= 0:
                raise ValueError("压测次数必须大于 0")

            try:
                interval = float(form.get("interval", "").strip())
            except ValueError as exc:
                raise ValueError("压测间隔必须是数字") from exc
            if interval < 0:
                raise ValueError("压测间隔不能小于 0")

            self.tester.start(url, count, interval)
            self._send_json({"ok": True, "state": self.state.snapshot()})
        except Exception as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=400)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def create_server() -> tuple[ThreadingHTTPServer, str]:
    state = LoadTestState()
    tester = LoadTester(state)

    class Handler(RequestHandler):
        pass

    Handler.state = state
    Handler.tester = tester

    bind_host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "0"))
    server = ThreadingHTTPServer((bind_host, port), Handler)
    actual_host, actual_port = server.server_address
    display_host = "localhost" if actual_host in {"0.0.0.0", "::"} else actual_host
    return server, f"http://{display_host}:{actual_port}"


def main() -> None:
    server, base_url = create_server()
    print(f"压测工具已启动：{base_url}")
    if os.getenv("OPEN_BROWSER", "auto").lower() in {"1", "true", "yes"}:
        webbrowser.open(base_url, new=1, autoraise=True)
        print("浏览器会自动打开；如果没有打开，请手动访问上面的地址。")
    elif os.getenv("OPEN_BROWSER", "auto").lower() == "auto" and os.getenv("HOST", "127.0.0.1") == "127.0.0.1":
        webbrowser.open(base_url, new=1, autoraise=True)
        print("浏览器会自动打开；如果没有打开，请手动访问上面的地址。")
    else:
        print("已禁用自动打开浏览器，请在宿主机浏览器中访问映射后的地址。")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n收到退出信号，正在关闭...")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
