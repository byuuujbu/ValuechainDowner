from __future__ import annotations

import re
from collections.abc import Callable
from decimal import Decimal
from typing import Any

import httpx

from app.data_providers.fmp import FinancialModelingPrepProvider
from app.data_providers.sec_edgar import SecEdgarClient, annual_facts_by_tag


def fmp_ticker_diagnostics(ticker: str) -> dict[str, object]:
    provider = FinancialModelingPrepProvider()
    symbol = ticker.upper()
    sections = {
        "profile": _capture(lambda: _profile_payload(provider, symbol)),
        "prices": _capture(lambda: _prices_payload(provider, symbol)),
        "fundamentals": _capture(lambda: _fundamentals_payload(provider, symbol)),
    }
    return {
        "ticker": symbol,
        "provider": "financialmodelingprep",
        "configured": provider.is_configured,
        "sections": sections,
    }


def sec_ticker_diagnostics(ticker: str) -> dict[str, object]:
    client = SecEdgarClient()
    symbol = ticker.upper()
    sections = {
        "cik": _capture(lambda: _sec_cik_payload(client, symbol)),
        "fundamental_facts": _capture(lambda: _sec_fundamental_payload(client, symbol)),
    }
    return {
        "ticker": symbol,
        "provider": "sec_edgar",
        "configured": client.is_configured,
        "sections": sections,
    }


def _capture(fn: Callable[[], dict[str, object]]) -> dict[str, object]:
    try:
        return {"ok": True, **fn()}
    except Exception as error:
        payload: dict[str, object] = {
            "ok": False,
            "error_type": error.__class__.__name__,
            "message": _redact_sensitive_url_params(str(error)),
        }
        if isinstance(error, httpx.HTTPStatusError):
            payload["status_code"] = error.response.status_code
            payload["response_preview"] = _redact_sensitive_url_params(error.response.text[:500])
        return payload


def _profile_payload(provider: FinancialModelingPrepProvider, ticker: str) -> dict[str, object]:
    asset = provider.get_asset(ticker)
    return {
        "asset": {
            "ticker": asset.ticker,
            "name": asset.name,
            "market": asset.market,
            "country": asset.country,
            "currency": asset.currency,
            "asset_type": asset.asset_type,
            "sector": asset.sector,
            "industry": asset.industry,
            "is_etf": asset.is_etf,
        }
    }


def _prices_payload(provider: FinancialModelingPrepProvider, ticker: str) -> dict[str, object]:
    prices = provider.get_daily_prices(ticker)
    latest_rows = prices[-5:]
    return {
        "row_count": len(prices),
        "latest_rows": [
            {
                "date": price.date.isoformat(),
                "open": _string_or_none(price.open),
                "high": _string_or_none(price.high),
                "low": _string_or_none(price.low),
                "close": _string_or_none(price.close),
                "adj_close": _string_or_none(price.adj_close),
                "volume": _string_or_none(price.volume),
                "data_source": price.data_source,
            }
            for price in latest_rows
        ],
    }


def _fundamentals_payload(provider: FinancialModelingPrepProvider, ticker: str) -> dict[str, object]:
    fundamentals = provider.get_fundamentals(ticker)
    latest_rows = fundamentals[-5:]
    return {
        "row_count": len(fundamentals),
        "latest_rows": [
            {
                "period_end": row.period_end.isoformat(),
                "period_type": row.period_type,
                "currency": row.currency,
                "revenue": _string_or_none(row.revenue),
                "operating_income": _string_or_none(row.operating_income),
                "net_income": _string_or_none(row.net_income),
                "total_assets": _string_or_none(row.total_assets),
                "total_equity": _string_or_none(row.total_equity),
                "total_debt": _string_or_none(row.total_debt),
                "operating_cash_flow": _string_or_none(row.operating_cash_flow),
                "capex": _string_or_none(row.capex),
                "free_cash_flow": _string_or_none(row.free_cash_flow),
                "shares_outstanding": _string_or_none(row.shares_outstanding),
                "data_source": row.data_source,
            }
            for row in latest_rows
        ],
    }


SEC_FACT_TAGS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"],
    "total_assets": ["Assets"],
    "total_equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "total_debt": ["LongTermDebtAndFinanceLeaseObligations", "LongTermDebt", "DebtCurrent"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "free_cash_flow": [],
    "shares_outstanding": ["EntityCommonStockSharesOutstanding", "WeightedAverageNumberOfDilutedSharesOutstanding"],
}


def _sec_cik_payload(client: SecEdgarClient, ticker: str) -> dict[str, object]:
    return {"cik": client.find_cik_by_ticker(ticker)}


def _sec_fundamental_payload(client: SecEdgarClient, ticker: str) -> dict[str, object]:
    cik = client.find_cik_by_ticker(ticker)
    companyfacts = client.companyfacts(cik)
    return {
        "cik": cik,
        "entity_name": companyfacts.get("entityName"),
        "fields": {
            field: _sec_field_payload(companyfacts, tags)
            for field, tags in SEC_FACT_TAGS.items()
        },
    }


def _sec_field_payload(companyfacts: dict[str, Any], tags: list[str]) -> dict[str, object]:
    if not tags:
        return {"ok": False, "reason": "derived_metric_not_direct_sec_tag", "tag": None, "latest_rows": []}
    for tag in tags:
        rows = annual_facts_by_tag(companyfacts, tag, unit="USD", limit=5)
        if not rows:
            rows = annual_facts_by_tag(companyfacts, tag, unit="shares", limit=5)
        if rows:
            return {
                "ok": True,
                "tag": tag,
                "latest_rows": [
                    {
                        "fiscal_year": row.get("fy"),
                        "period_end": row.get("end"),
                        "filed": row.get("filed"),
                        "form": row.get("form"),
                        "value": _string_or_none(row.get("val")),
                        "accession": row.get("accn"),
                        "frame": row.get("frame"),
                    }
                    for row in rows
                ],
            }
    return {"ok": False, "reason": "no_supported_annual_10k_fact", "tag": None, "latest_rows": []}


def _string_or_none(value: Decimal | Any | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _redact_sensitive_url_params(message: str) -> str:
    return re.sub(r"(?i)(apikey=)[^&'\")\s]+", r"\1<redacted>", message)
