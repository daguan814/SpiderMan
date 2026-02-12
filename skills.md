# SpiderMan 项目操作说明（给 Codex）

## 1. 数据库可访问说明
- 本项目数据库可直接连接（MySQL）。
- 连接信息：
  - Host: `127.0.0.1`
  - Port: `3306`
  - Database: `stock`
  - User: `root`
  - Password: `Lhf134652`
  - Charset: `utf8mb4`

## 2. 如何查看数据库结构

### 2.1 用 SQL 快速查看
```sql
SHOW TABLES;
DESCRIBE daily_kline;
DESCRIBE stock_basic;
SELECT MAX(trade_date) AS max_trade_date, COUNT(DISTINCT trade_date) AS trade_days FROM daily_kline;
```

### 2.2 用 Python（SQLAlchemy + pandas）查看
```python
import pandas as pd
from sqlalchemy import create_engine

DB_URI = "mysql+pymysql://root:Lhf134652@127.0.0.1:3306/stock?charset=utf8mb4"
engine = create_engine(DB_URI)

print(pd.read_sql("SHOW TABLES", engine))
print(pd.read_sql("DESCRIBE daily_kline", engine))
print(pd.read_sql("DESCRIBE stock_basic", engine))
```

## 3. Conda 环境与运行方式
- 用户使用的环境提示符：`(SpiderMan) PS C:\Users\Administrator\Documents\code\SpiderMan>`
- Conda 默认安装目录（本机已确认）：`C:\Users\Administrator\miniconda3`

### 3.1 在 PowerShell 激活环境
```powershell
& "C:\Users\Administrator\miniconda3\shell\condabin\conda-hook.ps1"
conda activate SpiderMan
```

### 3.2 进入项目目录
```powershell
cd C:\Users\Administrator\Documents\code\SpiderMan
```

### 3.3 运行项目内脚本示例
```powershell
python "股票分析\db\数据库检查.py"
python "股票分析\db\数据增量更新.py"
python "股票分析\分析\2025板块分析.py"
```

## 4. 编码注意
- 项目里部分中文注释显示乱码，通常是文件历史编码问题；脚本逻辑不受影响。
- 新增脚本优先使用 UTF-8 编码保存。
