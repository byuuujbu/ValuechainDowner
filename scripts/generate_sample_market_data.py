from __future__ import annotations

import csv
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
ASSETS_CSV = SAMPLE_DIR / "assets.csv"
PRICE_CSV = SAMPLE_DIR / "price_daily_sample.csv"
FUNDAMENTALS_CSV = SAMPLE_DIR / "fundamentals_sample.csv"

TRADING_DAYS = 260
END_DATE = date(2026, 5, 29)

PRICE_BASES = {
    "RKLB": Decimal("8.40"),
    "LMT": Decimal("465.00"),
    "NOC": Decimal("500.00"),
    "BA": Decimal("185.00"),
    "SPY": Decimal("525.00"),
    "QQQ": Decimal("455.00"),
    "KODEX200": Decimal("36500.00"),
    "KODEXKOSDAQ150": Decimal("13800.00"),
    "GOLD_PROXY": Decimal("2350.00"),
    "BTC_PROXY": Decimal("68000.00"),
}

VOLUME_BASES = {
    "RKLB": Decimal("12500000"),
    "LMT": Decimal("1150000"),
    "NOC": Decimal("850000"),
    "BA": Decimal("6200000"),
    "SPY": Decimal("72000000"),
    "QQQ": Decimal("49000000"),
    "KODEX200": Decimal("4100000"),
    "KODEXKOSDAQ150": Decimal("2800000"),
    "GOLD_PROXY": Decimal("950000"),
    "BTC_PROXY": Decimal("450000"),
}

FUNDAMENTALS = {
    "RKLB": (Decimal("245000000"), Decimal("-176000000"), Decimal("-182000000"), Decimal("1600000000"), Decimal("980000000"), Decimal("520000000"), Decimal("-78000000"), Decimal("-92000000"), Decimal("-170000000"), Decimal("515000000")),
    "LMT": (Decimal("67571000000"), Decimal("8507000000"), Decimal("6921000000"), Decimal("52740000000"), Decimal("10650000000"), Decimal("19300000000"), Decimal("7918000000"), Decimal("-1745000000"), Decimal("6173000000"), Decimal("239000000")),
    "NOC": (Decimal("39290000000"), Decimal("3920000000"), Decimal("2940000000"), Decimal("46600000000"), Decimal("12300000000"), Decimal("14500000000"), Decimal("3850000000"), Decimal("-1390000000"), Decimal("2460000000"), Decimal("151000000")),
    "BA": (Decimal("77794000000"), Decimal("-773000000"), Decimal("-2222000000"), Decimal("137000000000"), Decimal("-17800000000"), Decimal("52800000000"), Decimal("5960000000"), Decimal("-1700000000"), Decimal("4260000000"), Decimal("589000000")),
}


def main() -> None:
    assets = read_assets()
    write_prices(assets)
    write_fundamentals(assets)


def read_assets() -> list[dict[str, str]]:
    with ASSETS_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_prices(assets: list[dict[str, str]]) -> None:
    fieldnames = [
        "ticker",
        "market",
        "date",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
        "trading_value",
        "data_source",
    ]
    rows: list[dict[str, str]] = []
    dates = trading_dates(TRADING_DAYS, END_DATE)
    for asset in assets:
        ticker = asset["ticker"]
        base_price = PRICE_BASES[ticker]
        base_volume = VOLUME_BASES[ticker]
        for index, day in enumerate(dates):
            wave = Decimal((index % 17) - 8) / Decimal("1000")
            drift = Decimal(index) / Decimal("10000")
            close = money(base_price * (Decimal("1") + drift + wave))
            open_price = money(close * (Decimal("0.997") + Decimal(index % 5) / Decimal("1000")))
            high = money(max(open_price, close) * Decimal("1.012"))
            low = money(min(open_price, close) * Decimal("0.988"))
            volume = whole(base_volume * (Decimal("1") + Decimal(index % 11) / Decimal("100")))
            rows.append(
                {
                    "ticker": ticker,
                    "market": asset["market"],
                    "date": day.isoformat(),
                    "open": str(open_price),
                    "high": str(high),
                    "low": str(low),
                    "close": str(close),
                    "adj_close": str(close),
                    "volume": str(volume),
                    "trading_value": str(whole(close * volume)),
                    "data_source": "sample",
                }
            )

    with PRICE_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_fundamentals(assets: list[dict[str, str]]) -> None:
    fieldnames = [
        "ticker",
        "market",
        "currency",
        "period_end",
        "period_type",
        "revenue",
        "operating_income",
        "net_income",
        "total_assets",
        "total_equity",
        "total_debt",
        "operating_cash_flow",
        "capex",
        "free_cash_flow",
        "shares_outstanding",
        "data_source",
    ]
    rows: list[dict[str, str]] = []
    market_by_ticker = {asset["ticker"]: asset["market"] for asset in assets}
    currency_by_ticker = {asset["ticker"]: asset["currency"] for asset in assets}
    for ticker, values in FUNDAMENTALS.items():
        rows.append(
            {
                "ticker": ticker,
                "market": market_by_ticker[ticker],
                "currency": currency_by_ticker[ticker],
                "period_end": "2025-12-31",
                "period_type": "annual",
                "revenue": str(values[0]),
                "operating_income": str(values[1]),
                "net_income": str(values[2]),
                "total_assets": str(values[3]),
                "total_equity": str(values[4]),
                "total_debt": str(values[5]),
                "operating_cash_flow": str(values[6]),
                "capex": str(values[7]),
                "free_cash_flow": str(values[8]),
                "shares_outstanding": str(values[9]),
                "data_source": "sample",
            }
        )

    with FUNDAMENTALS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def trading_dates(count: int, end_date: date) -> list[date]:
    dates: list[date] = []
    cursor = end_date
    while len(dates) < count:
        if cursor.weekday() < 5:
            dates.append(cursor)
        cursor -= timedelta(days=1)
    return list(reversed(dates))


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def whole(value: Decimal) -> Decimal:
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


if __name__ == "__main__":
    main()
