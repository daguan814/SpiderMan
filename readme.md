# SpiderMan

一个以 Python 为主的个人脚本仓库，主要收集了日常使用过的小工具、数据处理脚本、学习平台自动化脚本，以及股票分析相关代码。

这个仓库不是单一应用，更接近“按场景整理的工具箱”。不同目录对应不同用途，运行方式和依赖也不完全相同。

## 项目结构

```text
SpiderMan
├─ 代码库
│  ├─ fly_code         # 无人机相关脚本
│  ├─ WuHanTTC         # 武汉相关学习平台脚本
│  ├─ sklearn          # 机器学习实验代码
│  ├─ 文字转像素        # 图片转文字像素画工具
│  ├─ 考号编排          # 学生考号/编号重排工具
│  └─ 鄂慧学习网        # 学习平台刷课/考试脚本
├─ 名师工作室           # 页面访问量相关脚本
├─ 股票分析
│  ├─ db              # 股票数据库更新/检查
│  └─ 分析             # 股票板块分析脚本
└─ .venv              # 本地虚拟环境
```

## 环境要求

- Python 3.10 及以上
- Windows 环境优先，部分脚本写法也更偏向 Windows 使用方式
- 建议使用虚拟环境运行

示例：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -U pip
```

部分脚本可能还需要额外安装依赖，例如：

```powershell
pip install requests pillow pandas sqlalchemy pymysql tushare
```

如果你要使用 Playwright 类脚本，可以额外执行：

```powershell
pip install playwright
playwright install
```

## 目录说明

### 1. `代码库/fly_code`

无人机任务脚本，依赖外部飞控运行环境和对应模块，例如 `helloFly`、`Service.print_map`、`Service.target_paths`。

当前可见脚本包括：

- `寻找任务点.py`
  用于起飞、按指定方向移动、搜索标签点、拍照并输出地图信息。
- `打靶.py`
  根据标签路径执行飞行、转向和射击动作。

说明：

- 这部分代码不能在普通 Python 环境中直接运行。
- 需要对应硬件、SDK 和运行平台支持。

### 2. `代码库/WuHanTTC`

学习平台自动化脚本。

- `whttc.py`
  使用 `requests` 模拟提交学习记录，请求时需要手动提供 `cookie`。

说明：

- 脚本里写死了部分请求头和参数。
- 平台接口、字段、课程区间如果变化，脚本需要同步调整。

### 3. `代码库/文字转像素`

一个相对完整的小工具，用来把图片渲染成“文字像素画”。

入口文件：

- `main.py`

依赖：

- `Pillow`

示例：

```powershell
cd "代码库\文字转像素"
python main.py -i input.jpg -o output.png -t "zyl"
```

使用字符集按明暗替换像素：

```powershell
python main.py -i input.jpg -o output.png --charset "@%#*+=-:. "
```

常用参数：

- `-i, --input`：输入图片路径
- `-o, --output`：输出图片路径
- `-t, --text`：用于替换像素的文字
- `--charset`：按亮度映射字符集
- `--invert`：反转字符亮度映射
- `--font`：指定字体文件
- `--font-size`：文字大小
- `--max-width` / `--max-height`：缩放输入图像

### 4. `代码库/考号编排`

用于根据 `students.txt` 中的班级和学生编号信息，重新排列输出顺序。

相关文件：

- `main.py`
- `students.txt`
- `out.txt`

`students.txt` 格式示例：

```text
1 420001
1 420002
2 430001
2 430002
```

运行方式：

```powershell
cd "代码库\考号编排"
python main.py
```

输出结果会写入当前目录下的 `out.txt`。

### 5. `代码库/鄂慧学习网`

学习平台自动化脚本，包含两类功能：

- 刷课
- 提交考试答案

入口文件：

- `main.py`

当前脚本特征：

- 需要手动配置 `token`
- 需要提前准备 `exam_id`
- 部分题目和答案映射写在脚本中
- 通过命令行交互选择“刷课”或“考试”

运行方式：

```powershell
cd "代码库\鄂慧学习网"
python main.py
```

### 6. `名师工作室`

- `访问量.py`
  通过反复请求页面和 `pageview` 接口来增加统计访问量。

依赖：

- `requests`

运行方式：

```powershell
cd "名师工作室"
python 访问量.py
```

### 7. `股票分析/db`

股票数据库维护脚本，主要基于 `Tushare + Pandas + SQLAlchemy + MySQL`。

当前脚本：

- `数据增量更新.py`
  根据数据库里已有的最新交易日，自动增量更新 `daily_kline` 数据。
- `数据库检查.py`
  检查数据库中的表结构、记录数、交易日覆盖范围和样例数据。

依赖：

- `tushare`
- `pandas`
- `sqlalchemy`
- `pymysql`

注意：

- 当前脚本中直接写了数据库连接信息和 Tushare token。
- 更建议后续改成环境变量或本地配置文件，不要直接提交敏感信息。

### 8. `股票分析/分析`

股票分析脚本，当前以板块统计和涨跌停分析为主。

已看到的脚本包括：

- `2025板块分析.py`
- `涨跌停板块分布.py`
- `涨跌停次日统计.py`

其中 `2025板块分析.py` 会：

- 从 `daily_kline` 读取 2025 年行情数据
- 结合 `stock_basic` 的行业字段
- 统计各行业年度涨跌幅
- 做简单去极值后输出行业表现结果

## 使用建议

- 这个仓库里很多脚本都带有明显的“个人使用”特点，运行前建议先检查脚本内的硬编码参数。
- 涉及账号、Cookie、Token、数据库密码的脚本，不建议直接对外公开。
- 涉及平台自动化的脚本，接口失效时优先检查请求头、认证字段、接口地址和时间参数。
- 涉及数据库的脚本，先确认本地 MySQL 中已经存在目标库和对应数据表。

## 后续可优化方向

- 增加统一的 `requirements.txt`
- 将敏感配置迁移到 `.env` 或配置文件
- 给每个子工具补独立 README
- 为可复用脚本增加命令行参数，而不是直接修改源码

## 说明

仓库内部分脚本和注释存在历史编码问题，使用编辑器统一转为 UTF-8 后会更方便维护。
