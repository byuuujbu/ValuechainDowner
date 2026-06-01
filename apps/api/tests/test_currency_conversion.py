from datetime import date
from decimal import Decimal

import pytest

from app.data_providers.interfaces import FundamentalsPeriod
from app.services.currency import convert_fundamentals_to_krw_millions


def test_convert_usd_fundamentals_to_krw_millions() -> None:
    converted = convert_fundamentals_to_krw_millions(
        FundamentalsPeriod(
            ticker="LMT",
            market="US",
            currency="USD",
            period_end=date(2025, 12, 31),
            period_type="annual",
            revenue=Decimal("67571000000"),
            operating_income=Decimal("8507000000"),
            net_income=Decimal("6921000000"),
            total_assets=Decimal("52740000000"),
            total_equity=Decimal("10650000000"),
            total_debt=Decimal("19300000000"),
            operating_cash_flow=Decimal("7918000000"),
            capex=Decimal("-1745000000"),
            free_cash_flow=Decimal("6173000000"),
            shares_outstanding=Decimal("239000000"),
            data_source="sample",
        ),
        usd_krw_rate=Decimal("1350"),
    )

    assert converted.unit == "million_krw"
    assert converted.revenue == Decimal("91220850.00")
    assert converted.free_cash_flow == Decimal("8333550.00")
    assert converted.capex == Decimal("-2355750.00")


def test_reject_non_usd_currency_until_fx_provider_exists() -> None:
    with pytest.raises(ValueError):
        convert_fundamentals_to_krw_millions(
            FundamentalsPeriod(
                ticker="KR",
                market="KR",
                currency="KRW",
                period_end=date(2025, 12, 31),
                period_type="annual",
                revenue=Decimal("1"),
                operating_income=None,
                net_income=None,
                total_assets=None,
                total_equity=None,
                total_debt=None,
                operating_cash_flow=None,
                capex=None,
                free_cash_flow=None,
                shares_outstanding=None,
                data_source="sample",
            ),
            usd_krw_rate=Decimal("1350"),
        )
