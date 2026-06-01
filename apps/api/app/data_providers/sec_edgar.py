from __future__ import annotations

from decimal import Decimal
from typing import Any

import httpx

from app.core.config import settings


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
