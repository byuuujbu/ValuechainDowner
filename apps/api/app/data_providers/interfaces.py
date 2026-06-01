from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class AssetProfile:
    ticker: str
    name: str
    market: str
    country: str | None
    currency: str | None
    asset_type: str
    sector: str | None
    industry: str | None
    is_etf: bool


@dataclass(frozen=True)
class DailyPrice:
    ticker: str
    market: str
    date: date
    open: Decimal | None
    high: Decimal | None
    low: Decimal | None
    close: Decimal
    adj_close: Decimal | None
    volume: Decimal | None
    trading_value: Decimal | None
    data_source: str


@dataclass(frozen=True)
class FundamentalsPeriod:
    ticker: str
    market: str
    currency: str | None
    period_end: date
    period_type: str
    revenue: Decimal | None
    operating_income: Decimal | None
    net_income: Decimal | None
    total_assets: Decimal | None
    total_equity: Decimal | None
    total_debt: Decimal | None
    operating_cash_flow: Decimal | None
    capex: Decimal | None
    free_cash_flow: Decimal | None
    shares_outstanding: Decimal | None
    data_source: str


class AssetReferenceProvider(Protocol):
    def list_assets(self) -> list[AssetProfile]:
        raise NotImplementedError

    def get_asset(self, ticker: str, market: str | None = None) -> AssetProfile:
        raise NotImplementedError


class MarketDataProvider(Protocol):
    def get_daily_prices(
        self,
        ticker: str,
        start_date: date | None = None,
        end_date: date | None = None,
        market: str | None = None,
    ) -> list[DailyPrice]:
        raise NotImplementedError


class FundamentalDataProvider(Protocol):
    def get_fundamentals(
        self,
        ticker: str,
        market: str | None = None,
    ) -> list[FundamentalsPeriod]:
        raise NotImplementedError
