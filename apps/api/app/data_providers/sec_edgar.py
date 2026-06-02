from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

import httpx

from app.core.config import settings


SEC_FACT_TAGS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"],
    "operating_income": ["OperatingIncomeLoss"],
    "net_income": ["NetIncomeLoss"],
    "total_assets": ["Assets"],
    "total_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "total_debt": ["LongTermDebtAndFinanceLeaseObligations", "LongTermDebt", "DebtCurrent"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "shares_outstanding": [
        "EntityCommonStockSharesOutstanding",
        "WeightedAverageNumberOfDilutedSharesOutstanding",
    ],
}


@dataclass(frozen=True)
class SecFactSource:
    tag: str
    unit: str
    period_end: date
    fiscal_year: int | None
    filed: date | None
    form: str | None
    accession: str | None
    frame: str | None
    original_value: Decimal
    normalized_value: Decimal


@dataclass(frozen=True)
class SecNormalizedFundamentalsPeriod:
    ticker: str
    market: str
    currency: str
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
    source_metadata: dict[str, SecFactSource | list[SecFactSource]]


class SecEdgarClient:
    def __init__(
        self,
        user_agent: str | None = None,
        client: httpx.Client | None = None,
        company_tickers_url: str | None = None,
        companyfacts_url_template: str | None = None,
    ) -> None:
        self.user_agent = user_agent if user_agent is not None else settings.sec_user_agent
        self.company_tickers_url = company_tickers_url or settings.sec_company_tickers_url
        self.companyfacts_url_template = (
            companyfacts_url_template or settings.sec_companyfacts_url_template
        )
        self.client = client or httpx.Client(timeout=20)

    @property
    def is_configured(self) -> bool:
        return bool(self.user_agent)

    def company_tickers(self) -> dict[str, Any]:
        return self._get(self.company_tickers_url)

    def find_cik_by_ticker(self, ticker: str) -> str:
        wanted = ticker.upper()
        for row in self.company_tickers().values():
            if str(row.get("ticker", "")).upper() == wanted:
                return normalize_cik(row["cik_str"])
        raise LookupError(f"SEC CIK not found for ticker={ticker}")

    def companyfacts(self, cik: str | int) -> dict[str, Any]:
        url = self.companyfacts_url_template.format(cik=normalize_cik(cik))
        return self._get(url)

    def _get(self, url: str) -> dict[str, Any]:
        if not self.user_agent:
            raise RuntimeError("SEC_USER_AGENT is required to call SEC EDGAR.")
        response = self.client.get(url, headers={"User-Agent": self.user_agent})
        response.raise_for_status()
        return response.json()


def normalize_cik(cik: str | int) -> str:
    digits = "".join(character for character in str(cik) if character.isdigit())
    if not digits:
        raise ValueError("CIK must contain at least one digit.")
    return digits.zfill(10)


def latest_annual_fact(
    companyfacts: dict[str, Any],
    tag: str,
    unit: str = "USD",
) -> tuple[Decimal, dict[str, Any]] | None:
    facts = companyfacts.get("facts", {}).get("us-gaap", {})
    units = facts.get(tag, {}).get("units", {})
    rows = [
        row
        for row in units.get(unit, [])
        if row.get("form") == "10-K" and row.get("val") is not None
    ]
    if not rows:
        return None
    latest = sorted(rows, key=lambda row: (row.get("end") or "", row.get("filed") or ""))[-1]
    return Decimal(str(latest["val"])), latest


def annual_facts_by_tag(
    companyfacts: dict[str, Any],
    tag: str,
    unit: str = "USD",
    limit: int = 5,
) -> list[dict[str, Any]]:
    facts = companyfacts.get("facts", {}).get("us-gaap", {})
    units = facts.get(tag, {}).get("units", {})
    rows = [
        row
        for row in units.get(unit, [])
        if row.get("form") == "10-K" and row.get("val") is not None and row.get("end")
    ]
    latest_by_end: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: (item.get("filed") or "", item.get("accn") or "")):
        latest_by_end[row["end"]] = row
    return sorted(
        latest_by_end.values(),
        key=lambda item: item.get("end") or "",
    )[-limit:]


def normalized_fundamentals_from_companyfacts(
    companyfacts: dict[str, Any],
    ticker: str,
    market: str = "US",
    currency: str = "USD",
    limit: int = 5,
) -> list[SecNormalizedFundamentalsPeriod]:
    rows_by_field = {
        field: _annual_sources_for_field(companyfacts, field, tags, currency)
        for field, tags in SEC_FACT_TAGS.items()
    }
    period_ends = sorted(
        {
            source.period_end
            for sources in rows_by_field.values()
            for source in sources
        }
    )[-limit:]

    periods: list[SecNormalizedFundamentalsPeriod] = []
    for period_end in period_ends:
        values: dict[str, Decimal | None] = {}
        metadata: dict[str, SecFactSource | list[SecFactSource]] = {}
        for field, sources in rows_by_field.items():
            source = next((item for item in sources if item.period_end == period_end), None)
            values[field] = source.normalized_value if source else None
            if source is not None:
                metadata[field] = source

        free_cash_flow = None
        if values.get("operating_cash_flow") is not None and values.get("capex") is not None:
            free_cash_flow = values["operating_cash_flow"] + values["capex"]
            metadata["free_cash_flow"] = [
                metadata["operating_cash_flow"],
                metadata["capex"],
            ]

        periods.append(
            SecNormalizedFundamentalsPeriod(
                ticker=ticker.upper(),
                market=market,
                currency=currency,
                period_end=period_end,
                period_type="annual",
                revenue=values.get("revenue"),
                operating_income=values.get("operating_income"),
                net_income=values.get("net_income"),
                total_assets=values.get("total_assets"),
                total_equity=values.get("total_equity"),
                total_debt=values.get("total_debt"),
                operating_cash_flow=values.get("operating_cash_flow"),
                capex=values.get("capex"),
                free_cash_flow=free_cash_flow,
                shares_outstanding=values.get("shares_outstanding"),
                data_source="sec_edgar_companyfacts",
                source_metadata=metadata,
            )
        )
    return periods


def _annual_sources_for_field(
    companyfacts: dict[str, Any],
    field: str,
    tags: list[str],
    currency: str,
) -> list[SecFactSource]:
    for tag in tags:
        unit = "shares" if field == "shares_outstanding" else currency
        rows = annual_facts_by_tag(companyfacts, tag, unit=unit, limit=10)
        if rows:
            return [_source_from_row(row, tag, unit, field) for row in rows]
    return []


def _source_from_row(
    row: dict[str, Any],
    tag: str,
    unit: str,
    field: str,
) -> SecFactSource:
    original_value = Decimal(str(row["val"]))
    normalized_value = -original_value if field == "capex" else original_value
    return SecFactSource(
        tag=tag,
        unit=unit,
        period_end=date.fromisoformat(row["end"]),
        fiscal_year=row.get("fy"),
        filed=date.fromisoformat(row["filed"]) if row.get("filed") else None,
        form=row.get("form"),
        accession=row.get("accn"),
        frame=row.get("frame"),
        original_value=original_value,
        normalized_value=normalized_value,
    )
