from datetime import date
from decimal import Decimal

import pytest

from app.data_providers import AssetReferenceProvider, FundamentalDataProvider, MarketDataProvider
from app.data_providers.sample_csv import SampleCsvDataProvider


def test_sample_provider_satisfies_interfaces() -> None:
    provider = SampleCsvDataProvider()

    asset_provider: AssetReferenceProvider = provider
    market_provider: MarketDataProvider = provider
    fundamental_provider: FundamentalDataProvider = provider

    assert len(asset_provider.list_assets()) == 10
    assert market_provider.get_daily_prices("RKLB")
    assert fundamental_provider.get_fundamentals("RKLB")


def test_sample_provider_lists_etfs_and_common_stocks() -> None:
    provider = SampleCsvDataProvider()

    assets = provider.list_assets()
    etfs = [asset for asset in assets if asset.is_etf]
    common_stocks = [asset for asset in assets if asset.asset_type == "common_stock"]

    assert {asset.ticker for asset in common_stocks} == {"RKLB", "LMT", "NOC", "BA"}
    assert {"SPY", "QQQ", "KODEX200", "KODEXKOSDAQ150"}.issubset(
        {asset.ticker for asset in etfs}
    )


def test_sample_provider_returns_minimum_260_daily_prices() -> None:
    provider = SampleCsvDataProvider()

    prices = provider.get_daily_prices("RKLB")

    assert len(prices) == 260
    assert prices == sorted(prices, key=lambda price: price.date)
    assert all(price.close > 0 for price in prices)
    assert all(price.trading_value is not None and price.trading_value > 0 for price in prices)


def test_sample_provider_filters_prices_by_date_range() -> None:
    provider = SampleCsvDataProvider()

    prices = provider.get_daily_prices(
        "SPY",
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 29),
    )

    assert prices
    assert prices[0].date >= date(2026, 5, 1)
    assert prices[-1].date <= date(2026, 5, 29)


def test_sample_provider_returns_common_stock_fundamentals() -> None:
    provider = SampleCsvDataProvider()

    fundamentals = provider.get_fundamentals("LMT")

    assert len(fundamentals) == 1
    assert fundamentals[0].period_type == "annual"
    assert fundamentals[0].revenue == Decimal("67571000000")
    assert fundamentals[0].free_cash_flow == Decimal("6173000000")


def test_sample_provider_returns_no_fundamentals_for_etf() -> None:
    provider = SampleCsvDataProvider()

    assert provider.get_fundamentals("SPY") == []


def test_sample_provider_raises_for_unknown_asset() -> None:
    provider = SampleCsvDataProvider()

    with pytest.raises(LookupError):
        provider.get_asset("NOPE")
