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


def analyze_limit_events_follow(
    days: int = 30,
    up_threshold: float = 9.9,
    down_threshold: float = -9.9,
) -> None:
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
        ),
        event_with_next_date AS (
            SELECT
                e.event_type,
                e.ts_code,
                e.trade_date,
                (
                    SELECT MIN(x.trade_date)
                    FROM daily_kline x
                    WHERE x.ts_code = e.ts_code
                      AND x.trade_date > e.trade_date
                ) AS next_trade_date
            FROM limit_events e
        )
        SELECT
            e.event_type,
            COUNT(*) AS event_count,
            COALESCE(SUM(n.pct_chg > 0), 0) AS next_up_events,
            COALESCE(SUM(n.pct_chg < 0), 0) AS next_down_events,
            COALESCE(SUM(n.pct_chg = 0), 0) AS next_flat_events,
            COALESCE(SUM(n.pct_chg IS NULL), 0) AS next_missing_events,
            COALESCE(SUM(n.pct_chg >= :up_threshold), 0) AS next_limit_up_events,
            COALESCE(SUM(n.pct_chg <= :down_threshold), 0) AS next_limit_down_events,
            AVG(CASE WHEN n.pct_chg > 0 THEN n.pct_chg END) AS next_up_avg_pct,
            AVG(CASE WHEN n.pct_chg < 0 THEN n.pct_chg END) AS next_down_avg_pct
        FROM event_with_next_date e
        LEFT JOIN daily_kline n
            ON n.ts_code = e.ts_code
           AND n.trade_date = e.next_trade_date
        GROUP BY e.event_type
        """
    )

    df = pd.read_sql(
        sql,
        engine,
        params={
            "days": days,
            "up_threshold": up_threshold,
            "down_threshold": down_threshold,
        },
    )

    if df.empty:
        print(f"最近{days}个交易日内没有满足涨停/跌停阈值的记录。")
        return

    print(f"统计区间: 最近{days}个交易日")
    print(f"涨停判定: pct_chg >= {up_threshold}")
    print(f"跌停判定: pct_chg <= {down_threshold}")
    print("=" * 50)
    print("说明: 仅事件次数口径（同一股票多次涨/跌停会重复计数）")
    print("-" * 50)

    for event_type in ["UP", "DOWN"]:
        row = df[df["event_type"] == event_type]
        if row.empty:
            label = "涨停" if event_type == "UP" else "跌停"
            print(f"{label}统计: 无记录")
            print("-" * 50)
            continue

        r = row.iloc[0]
        label = "涨停" if event_type == "UP" else "跌停"

        print(f"{label}统计:")
        print(f"事件总次数: {int(r['event_count'])}")
        print(f"次日上涨 - 事件次数: {int(r['next_up_events'])}")
        print(f"次日下跌 - 事件次数: {int(r['next_down_events'])}")
        print(f"次日平盘 - 事件次数: {int(r['next_flat_events'])}")
        print(f"次日缺失 - 事件次数: {int(r['next_missing_events'])}")
        up_avg = r["next_up_avg_pct"]
        down_avg = r["next_down_avg_pct"]
        up_avg_text = f"{up_avg:.4f}%" if pd.notna(up_avg) else "N/A"
        down_avg_text = f"{down_avg:.4f}%" if pd.notna(down_avg) else "N/A"
        print(f"次日上涨 - 平均涨幅: {up_avg_text}")
        print(f"次日下跌 - 平均跌幅: {down_avg_text}")
        print("-" * 50)

    up_row = df[df["event_type"] == "UP"]
    down_row = df[df["event_type"] == "DOWN"]

    up_to_up = int(up_row.iloc[0]["next_limit_up_events"]) if not up_row.empty else 0
    up_to_down = int(up_row.iloc[0]["next_limit_down_events"]) if not up_row.empty else 0
    down_to_up = int(down_row.iloc[0]["next_limit_up_events"]) if not down_row.empty else 0
    down_to_down = int(down_row.iloc[0]["next_limit_down_events"]) if not down_row.empty else 0

    print("极端事件次日延续/反转统计（事件次数）:")
    print(f"涨停后涨停: {up_to_up}")
    print(f"涨停后跌停: {up_to_down}")
    print(f"跌停后涨停: {down_to_up}")
    print(f"跌停后跌停: {down_to_down}")
    print("-" * 50)


def main():
    parser = argparse.ArgumentParser(description="统计最近N个交易日涨停/跌停后次日涨跌情况")
    parser.add_argument("--days", type=int, default=30, help="统计最近多少个交易日，默认30")
    parser.add_argument(
        "--up-threshold",
        type=float,
        default=9.9,
        help="涨停判定阈值，默认9.9（按pct_chg）",
    )
    parser.add_argument(
        "--down-threshold",
        type=float,
        default=-9.9,
        help="跌停判定阈值，默认-9.9（按pct_chg）",
    )
    args = parser.parse_args()

    analyze_limit_events_follow(
        days=args.days,
        up_threshold=args.up_threshold,
        down_threshold=args.down_threshold,
    )


if __name__ == "__main__":
    main()
