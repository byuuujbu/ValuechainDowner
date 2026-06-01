from __future__ import annotations

from decimal import Decimal

import httpx
from fastapi.testclient import TestClient

from app.data_providers.fmp import FinancialModelingPrepProvider
from app.data_providers.sec_edgar import latest_annual_fact, normalize_cik
from app.main import app


def test_data_provider_status_does_not_expose_secrets() -> None:
    response = TestClient(app).get("/data-providers/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["active_provider"] == "sample_csv"
    assert payload["sample_available"] is True
    assert "api_key" not in str(payload).lower()


def test_fmp_provider_normalizes_profile_and_prices() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["apikey"] == "test-key"
        if request.url.path.endswith("/profile/RKLB"):
            return httpx.Response(
                200,
                json=[
                    {
                        "symbol": "RKLB",
                        "companyName": "Rocket Lab USA, Inc.",
                        "exchangeShortName": "NASDAQ",
                        "country": "US",
                        "currency": "USD",
                        "sector": "Industrials",
                        "industry": "Aerospace & Defense",
                        "isEtf": False,
                    }
                ],
            )
        if request.url.path.endswith("/historical-price-full/RKLB"):
            return httpx.Response(
                200,
                json={
                    "historical": [
                        {
                            "date": "2026-05-30",
                            "open": 10,
                            "high": 11,
                            "low": 9,
                            "close": 10.5,
                            "adjClose": 10.4,
                            "volume": 1000,
                        }
                    ]
                },
            )
        return httpx.Response(404)

    provider = FinancialModelingPrepProvider(
        api_key="test-key",
        base_url="https://example.test/api/v3",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    asset = provider.get_asset("RKLB")
    prices = provider.get_daily_prices("RKLB")

    assert asset.name == "Rocket Lab USA, Inc."
    assert asset.market == "NASDAQ"
    assert prices[0].close == Decimal("10.5")
    assert prices[0].data_source == "financialmodelingprep"


def test_fmp_provider_merges_financial_statement_rows_by_period_date() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/income-statement/LMT"):
            return httpx.Response(
                200,
                json=[
                    {
                        "date": "2025-12-31",
                        "period": "FY",
                        "reportedCurrency": "USD",
                        "revenue": 100,
                        "operatingIncome": 20,
                        "netIncome": 12,
                        "weightedAverageShsOutDil": 5,
                    }
                ],
            )
        if request.url.path.endswith("/balance-sheet-statement/LMT"):
            return httpx.Response(
                200,
                json=[
                    {
                        "date": "2025-12-31",
                        "totalAssets": 300,
                        "totalStockholdersEquity": 80,
                        "totalDebt": 40,
                    }
                ],
            )
        if request.url.path.endswith("/cash-flow-statement/LMT"):
            return httpx.Response(
                200,
                json=[
                    {
                        "date": "2025-12-31",
                        "operatingCashFlow": 30,
                        "capitalExpenditure": -8,
                        "freeCashFlow": 22,
                    }
                ],
            )
        return httpx.Response(404)

    provider = FinancialModelingPrepProvider(
        api_key="test-key",
        base_url="https://example.test/api/v3",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    fundamentals = provider.get_fundamentals("LMT")

    assert len(fundamentals) == 1
    assert fundamentals[0].period_type == "annual"
    assert fundamentals[0].revenue == Decimal("100")
    assert fundamentals[0].total_assets == Decimal("300")
    assert fundamentals[0].free_cash_flow == Decimal("22")


def test_sec_helpers_normalize_cik_and_extract_latest_annual_fact() -> None:
    companyfacts = {
        "facts": {
            "us-gaap": {
                "Revenues": {
                    "units": {
                        "USD": [
                            {"form": "10-K", "end": "2024-12-31", "filed": "2025-02-01", "val": 90},
                            {"form": "10-Q", "end": "2025-03-31", "filed": "2025-05-01", "val": 30},
                            {"form": "10-K", "end": "2025-12-31", "filed": "2026-02-01", "val": 100},
                        ]
                    }
                }
            }
        }
    }

    result = latest_annual_fact(companyfacts, "Revenues")

    assert normalize_cik("320193") == "0000320193"
    assert result is not None
    assert result[0] == Decimal("100")
    assert result[1]["end"] == "2025-12-31"
