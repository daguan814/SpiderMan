import sqlite3
import pandas as pd

DB_PATH = "db/stock.db"
conn = sqlite3.connect(DB_PATH)

# =========================
# 1. 最近 3 个交易日
# =========================
dates = pd.read_sql(
    """
    SELECT DISTINCT trade_date
    FROM daily_kline
    ORDER BY trade_date DESC
    LIMIT 3;
    """,
    conn
)["trade_date"].tolist()

today = dates[0]
prev_2_days = dates[1:]  # 最近3天，去掉今天的前两天

print("判断下跌行情的交易日：", dates)
print("今日：", today)

# =========================
# 2. 最近3天总体下跌（收盘价呈下降趋势）
# =========================
price_df = pd.read_sql(
    f"""
    SELECT ts_code, trade_date, close
    FROM daily_kline
    WHERE trade_date IN ({','.join("'" + d + "'" for d in dates)})
    """,
    conn
)

price_pivot = price_df.pivot(index="ts_code", columns="trade_date", values="close")
price_pivot = price_pivot.dropna()

# 正确判断近3天收盘价下降趋势
downtrend_codes = set(
    price_pivot[
        (price_pivot[dates[2]] > price_pivot[dates[1]]) &
        (price_pivot[dates[1]] > price_pivot[dates[0]])
    ].index
)
print(f"\n近3天总体下跌股票数：{len(downtrend_codes)}")

# =========================
# 3. 今日锤子线
# =========================
today_df = pd.read_sql(
    f"""
    SELECT
        ts_code,
        open,
        high,
        low,
        close,
        pre_close
    FROM daily_kline
    WHERE trade_date = '{today}'
    """,
    conn
)

today_df["body"] = (today_df["close"] - today_df["open"]).abs()
today_df["lower_shadow"] = today_df[["open", "close"]].min(axis=1) - today_df["low"]
today_df["upper_shadow"] = today_df["high"] - today_df[["open", "close"]].max(axis=1)

hammer_df = today_df[
    (today_df["lower_shadow"] >= 2 * today_df["body"]) &
    (today_df["upper_shadow"] <= today_df["body"])
]

hammer_codes = set(hammer_df["ts_code"])
print(f"今日锤子线股票数：{len(hammer_codes)}")

# =========================
# 4. 交集
# =========================
target_codes = downtrend_codes & hammer_codes
print(f"\n🔥 近3天下跌行情中今日出现锤子线：{len(target_codes)} 只")

if not target_codes:
    print("暂无符合条件的股票")
else:
    result = pd.read_sql(
        f"""
        SELECT
            d.ts_code,
            b.name AS 股票名称,
            d.open,
            d.high,
            d.low,
            d.close
        FROM daily_kline d
        JOIN stock_basic b
            ON d.ts_code = b.ts_code
        WHERE d.trade_date = '{today}'
          AND d.ts_code IN ({','.join("'" + c + "'" for c in target_codes)})
        ORDER BY b.name;
        """,
        conn
    )

    print("\n====== 结果股票 ======")
    print(result)

conn.close()
