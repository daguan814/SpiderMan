# 压测工具

一个简单的 Python 压测小工具，使用本地网页 GUI 展示界面，按顺序发送 `GET` 请求访问目标网址。

## 功能

- 输入网址
- 输入压测次数
- 输入压测间隔，单位为秒
- 点击开始后自动执行
- 支持停止
- 运行日志实时显示

## 运行

```bash
python3 压测工具/main.py
```

启动后会自动打开浏览器页面。如果没有自动打开，请手动访问终端里打印的本地地址。

## Docker 运行

```bash
docker build -t loadtest-gui ./压测工具
docker run --rm -p 8082:8082 loadtest-gui
```

然后在宿主机浏览器访问：

```text
http://localhost:8082
```

如果你想改端口：

```bash
docker run --rm -e PORT=8082 -p 8082:8082 loadtest-gui
```

## 说明

请只对你有权限测试的目标使用。
