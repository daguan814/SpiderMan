# AGENTS.md

## 项目名称
SpiderMan

## 目标
本文件为本仓库内 Agent（含 Codex）提供统一、可执行的项目操作规范。

## 工作目录
- 仓库路径：`C:\Users\Administrator\Documents\code\SpiderMan`
- 默认在仓库根目录执行命令。

## 运行环境
- Shell：PowerShell
- Conda 安装目录：`C:\Users\Administrator\miniconda3`
- 推荐环境：`SpiderMan`

### 激活环境（PowerShell）
```powershell
& "C:\Users\Administrator\miniconda3\shell\condabin\conda-hook.ps1"
conda activate SpiderMan
cd C:\Users\Administrator\Documents\code\SpiderMan
```

## 数据库连接（MySQL）
- Host: `127.0.0.1`
- Port: `3306`
- Database: `stock`
- User: `root`
- Password: `Lhf134652`
- Charset: `utf8mb4`

### 快速检查 SQL
```sql
SHOW TABLES;
DESCRIBE daily_kline;
DESCRIBE stock_basic;
SELECT MAX(trade_date) AS max_trade_date, COUNT(DISTINCT trade_date) AS trade_days FROM daily_kline;
```

### Python 检查示例（SQLAlchemy + pandas）
```python
import pandas as pd
from sqlalchemy import create_engine

DB_URI = "mysql+pymysql://root:Lhf134652@127.0.0.1:3306/stock?charset=utf8mb4"
engine = create_engine(DB_URI)

print(pd.read_sql("SHOW TABLES", engine))
print(pd.read_sql("DESCRIBE daily_kline", engine))
print(pd.read_sql("DESCRIBE stock_basic", engine))
```

## 常用脚本
```powershell
python "股票分析\db\数据库检查.py"
python "股票分析\db\数据增量更新.py"
python "股票分析\分析\2025板块分析.py"
```

## 编码与文件规范
- 新增或修改文件统一使用 UTF-8 编码。
- 历史文件可能存在中文乱码（编码遗留问题），优先保证逻辑正确性，不做无关大规模重编码。

## 执行原则（Agent）
- 优先最小改动，避免影响现有流程。
- 先确认依赖与路径，再运行脚本。
- 涉及数据库写入操作前，先说明影响范围。
- 未经明确要求，不执行破坏性操作（如批量删除、重置）。
