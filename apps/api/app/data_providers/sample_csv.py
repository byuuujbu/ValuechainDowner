from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.data_providers.interfaces import AssetProfile, DailyPrice, FundamentalsPeriod


def _default_sample_dir() -> Path:
    for parent in Path(__file__).resolve().parents:
        sample_dir = parent / "data" / "sample"
        if sample_dir.exists():
            return sample_dir
    return Path("data") / "sample"


DEFAULT_SAMPLE_DIR = _default_sample_dir()


class SampleCsvDataProvider:
    def __init__(self, sample_dir: Path = DEFAULT_SAMPLE_DIR) -> None:
        self.sample_dir = sample_dir

    def list_assets(self) -> list[AssetProfile]:
        return [
            AssetProfile(
                ticker=row["ticker"],
                name=row["name"],
                market=row["market"],
                country=row["country"] or None,
                currency=row["currency"] or None,
                asset_type=row["asset_type"],
                sector=row["sector"] or None,
                industry=row["industry"] or None,
                is_etf=_parse_bool(row["is_etf"]),
            )
            for row in self._read_csv("assets.csv")
        ]

    def get_asset(self, ticker: str, market: str | None = None) -> AssetProfile:
        ticker = ticker.upper()
        for asset in self.list_assets():
            if asset.ticker.upper() == ticker and (market is None or asset.market == market):
                return asset
        raise LookupError(f"Asset not found: ticker={ticker}, market={market}")

    def get_daily_prices(
        self,
        ticker: str,
        start_date: date | None = None,
        end_date: date | None = None,
        market: str | None = None,
    ) -> list[DailyPrice]:
        ticker = ticker.upper()
        prices: list[DailyPrice] = []
        for row in self._read_csv("price_daily_sample.csv"):
            row_date = date.fromisoformat(row["date"])
            if row["ticker"].upper() != ticker:
                continue
            if market is not None and row["market"] != market:
                continue
            if start_date is not None and row_date < start_date:
                continue
            if end_date is not None and row_date > end_date:
                continue

            prices.append(
                DailyPrice(
                    ticker=row["ticker"],
                    market=row["market"],
                    date=row_date,
                    open=_decimal_or_none(row["open"]),
                    high=_decimal_or_none(row["high"]),
                    low=_decimal_or_none(row["low"]),
                    close=Decimal(row["close"]),
                    adj_close=_decimal_or_none(row["adj_close"]),
                    volume=_decimal_or_none(row["volume"]),
                    trading_value=_decimal_or_none(row["trading_value"]),
                    data_source=row["data_source"],
                )
            )
        return prices

    def get_fundamentals(
        self,
        ticker: str,
        market: str | None = None,
    ) -> list[FundamentalsPeriod]:
        ticker = ticker.upper()
        periods: list[FundamentalsPeriod] = []
        for row in self._read_csv("fundamentals_sample.csv"):
            if row["ticker"].upper() != ticker:
                continue
            if market is not None and row["market"] != market:
                continue

            periods.append(
                FundamentalsPeriod(
                    ticker=row["ticker"],
                    market=row["market"],
                    currency=row.get("currency") or None,
                    period_end=date.fromisoformat(row["period_end"]),
                    period_type=row["period_type"],
                    revenue=_decimal_or_none(row["revenue"]),
                    operating_income=_decimal_or_none(row["operating_income"]),
                    net_income=_decimal_or_none(row["net_income"]),
                    total_assets=_decimal_or_none(row["total_assets"]),
                    total_equity=_decimal_or_none(row["total_equity"]),
                    total_debt=_decimal_or_none(row["total_debt"]),
                    operating_cash_flow=_decimal_or_none(row["operating_cash_flow"]),
                    capex=_decimal_or_none(row["capex"]),
                    free_cash_flow=_decimal_or_none(row["free_cash_flow"]),
                    shares_outstanding=_decimal_or_none(row["shares_outstanding"]),
                    data_source=row["data_source"],
                )
            )
        return periods

    def _read_csv(self, filename: str) -> list[dict[str, str]]:
        with (self.sample_dir / filename).open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))


def _decimal_or_none(value: str) -> Decimal | None:
    return Decimal(value) if value else None


def _parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"
