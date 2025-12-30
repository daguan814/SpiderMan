import sqlite3
import pandas as pd

DB_PATH = "stock.db"

conn = sqlite3.connect(DB_PATH)

print("========== 1. 数据库中的表 ==========")
tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)
print(tables)

print("\n========== 2. daily_kline 字段结构 ==========")
columns = pd.read_sql(
    "PRAGMA table_info(daily_kline);",
    conn
)
print(columns[["name", "type"]])

print("\n========== 3. 日线总记录数 ==========")
total_rows = pd.read_sql(
    "SELECT COUNT(*) AS 记录数 FROM daily_kline;",
    conn
)
print(total_rows)

print("\n========== 4. 股票数量 ==========")
stock_cnt = pd.read_sql(
    "SELECT COUNT(DISTINCT ts_code) AS 股票数 FROM daily_kline;",
    conn
)
print(stock_cnt)

print("\n========== 5. 覆盖的交易日 ==========")
date_range = pd.read_sql(
    """
    SELECT 
        MIN(trade_date) AS 最早日期,
        MAX(trade_date) AS 最晚日期,
        COUNT(DISTINCT trade_date) AS 交易日数量
    FROM daily_kline;
    """,
    conn
)
print(date_range)

print("\n========== 6. 每只股票的数据天数分布 ==========")
days_per_stock = pd.read_sql(
    """
    SELECT 
        ts_code,
        COUNT(*) AS 天数
    FROM daily_kline
    GROUP BY ts_code
    ORDER BY 天数;
    """,
    conn
)

print("最少数据的股票：")
print(days_per_stock.head(10))

print("\n--- 天数分布统计 ---")
print(days_per_stock["天数"].value_counts().sort_index())

print("\n========== 7. JOIN 股票名称抽样 ==========")
sample = pd.read_sql(
    """
    SELECT 
        d.ts_code,
        b.name AS 股票名称,
        d.trade_date,
        d.close
    FROM daily_kline d
    LEFT JOIN stock_basic b
        ON d.ts_code = b.ts_code
    ORDER BY d.trade_date DESC
    LIMIT 10;
    """,
    conn
)
print(sample)

conn.close()
