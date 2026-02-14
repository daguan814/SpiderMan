import argparse
import pandas as pd
from sqlalchemy import create_engine, text

DB_CONFIG = {
    "user": "root",
    "password": "Lhf134652",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "stock",
    "charset": "utf8mb4",
}


def get_engine():
    uri = (
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
        f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        f"?charset={DB_CONFIG['charset']}"
    )
    return create_engine(uri)


def fetch_industry_distribution(days: int, up_threshold: float, down_threshold: float) -> pd.DataFrame:
    engine = get_engine()
    sql = text(
        """
        WITH latest_dates AS (
            SELECT DISTINCT trade_date
            FROM daily_kline
            ORDER BY trade_date DESC
            LIMIT :days
        ),
        limit_events AS (
            SELECT ts_code, trade_date, 'UP' AS event_type
            FROM daily_kline
            WHERE pct_chg >= :up_threshold
              AND trade_date IN (SELECT trade_date FROM latest_dates)
            UNION ALL
            SELECT ts_code, trade_date, 'DOWN' AS event_type
            FROM daily_kline
            WHERE pct_chg <= :down_threshold
              AND trade_date IN (SELECT trade_date FROM latest_dates)
        )
        SELECT
            e.event_type,
            COALESCE(NULLIF(TRIM(b.industry), ''), '未知板块') AS industry,
            COUNT(*) AS event_count,
            COUNT(DISTINCT e.ts_code) AS stock_count
        FROM limit_events e
        LEFT JOIN stock_basic b
            ON e.ts_code COLLATE utf8mb4_unicode_ci = b.ts_code COLLATE utf8mb4_unicode_ci
        GROUP BY e.event_type, COALESCE(NULLIF(TRIM(b.industry), ''), '未知板块')
        """
    )

    return pd.read_sql(
        sql,
        engine,
        params={
            "days": days,
            "up_threshold": up_threshold,
            "down_threshold": down_threshold,
        },
    )


def print_top(df: pd.DataFrame, event_type: str, top_n: int) -> None:
    label = "涨停" if event_type == "UP" else "跌停"
    sub = df[df["event_type"] == event_type].copy()
    if sub.empty:
        print(f"{label}板块分布: 无数据")
        print("-" * 70)
        return

    sub = sub.sort_values(["event_count", "stock_count"], ascending=False).head(top_n)
    print(f"{label}板块分布 TOP {top_n}（按事件次数）")
    print(sub[["industry", "event_count", "stock_count"]].to_string(index=False))
    print("-" * 70)


def main():
    parser = argparse.ArgumentParser(description="统计涨停/跌停事件主要集中板块")
    parser.add_argument("--days", type=int, default=30, help="统计最近多少个交易日，默认30")
    parser.add_argument("--top", type=int, default=15, help="输出前多少个板块，默认15")
    parser.add_argument("--up-threshold", type=float, default=9.9, help="涨停判定阈值，默认9.9")
    parser.add_argument("--down-threshold", type=float, default=-9.9, help="跌停判定阈值，默认-9.9")
    args = parser.parse_args()

    df = fetch_industry_distribution(args.days, args.up_threshold, args.down_threshold)
    if df.empty:
        print(f"最近{args.days}个交易日没有涨停/跌停事件。")
        return

    print(f"统计区间: 最近{args.days}个交易日")
    print(f"涨停阈值: pct_chg >= {args.up_threshold}")
    print(f"跌停阈值: pct_chg <= {args.down_threshold}")
    print("=" * 70)

    print_top(df, "UP", args.top)
    print_top(df, "DOWN", args.top)


if __name__ == "__main__":
    main()
