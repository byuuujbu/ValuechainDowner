from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from app.data_providers.interfaces import FundamentalsPeriod

KRW_MILLION = Decimal("1000000")


@dataclass(frozen=True)
class ConvertedFundamentals:
    ticker: str
    source_currency: str
    target_currency: str
    fx_rate: Decimal
    unit: str
    revenue: Decimal | None
    operating_income: Decimal | None
    net_income: Decimal | None
    total_assets: Decimal | None
    total_equity: Decimal | None
    total_debt: Decimal | None
    operating_cash_flow: Decimal | None
    capex: Decimal | None
    free_cash_flow: Decimal | None


def convert_fundamentals_to_krw_millions(
    fundamentals: FundamentalsPeriod,
    *,
    usd_krw_rate: Decimal,
) -> ConvertedFundamentals:
    source_currency = fundamentals.currency or "USD"
    if source_currency != "USD":
        raise ValueError(f"Unsupported source currency for KRW conversion: {source_currency}")

    return ConvertedFundamentals(
        ticker=fundamentals.ticker,
        source_currency=source_currency,
        target_currency="KRW",
        fx_rate=usd_krw_rate,
        unit="million_krw",
        revenue=_usd_to_krw_million(fundamentals.revenue, usd_krw_rate),
        operating_income=_usd_to_krw_million(fundamentals.operating_income, usd_krw_rate),
        net_income=_usd_to_krw_million(fundamentals.net_income, usd_krw_rate),
        total_assets=_usd_to_krw_million(fundamentals.total_assets, usd_krw_rate),
        total_equity=_usd_to_krw_million(fundamentals.total_equity, usd_krw_rate),
        total_debt=_usd_to_krw_million(fundamentals.total_debt, usd_krw_rate),
        operating_cash_flow=_usd_to_krw_million(fundamentals.operating_cash_flow, usd_krw_rate),
        capex=_usd_to_krw_million(fundamentals.capex, usd_krw_rate),
        free_cash_flow=_usd_to_krw_million(fundamentals.free_cash_flow, usd_krw_rate),
    )


def _usd_to_krw_million(value: Decimal | None, usd_krw_rate: Decimal) -> Decimal | None:
    if value is None:
        return None
    return (value * usd_krw_rate / KRW_MILLION).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def usd_to_krw_million(value: Decimal | None, usd_krw_rate: Decimal) -> Decimal | None:
    return _usd_to_krw_million(value, usd_krw_rate)
