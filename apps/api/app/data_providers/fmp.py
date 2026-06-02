from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import httpx

from app.core.config import settings
from app.data_providers.interfaces import AssetProfile, DailyPrice, FundamentalsPeriod


class FinancialModelingPrepProvider:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.fmp_api_key
        self.base_url = _stable_base_url(base_url or settings.fmp_base_url)
        self.client = client or httpx.Client(timeout=20)

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def list_assets(self) -> list[AssetProfile]:
        raise NotImplementedError("FMP universe discovery is intentionally configured separately.")

    def get_asset(self, ticker: str, market: str | None = None) -> AssetProfile:
        payload = self._get("profile", params={"symbol": ticker.upper()})
        if not payload:
            raise LookupError(f"FMP asset not found: ticker={ticker}")
        row = payload[0]
        return AssetProfile(
            ticker=row.get("symbol", ticker).upper(),
            name=row.get("companyName") or ticker.upper(),
            market=market or row.get("exchangeShortName") or "US",
            country=row.get("country"),
            currency=row.get("currency"),
            asset_type="etf" if row.get("isEtf") else "common_stock",
            sector=row.get("sector"),
            industry=row.get("industry"),
            is_etf=bool(row.get("isEtf")),
        )

    def get_daily_prices(
        self,
        ticker: str,
        start_date: date | None = None,
        end_date: date | None = None,
        market: str | None = None,
    ) -> list[DailyPrice]:
        params: dict[str, str] = {}
        if start_date is not None:
            params["from"] = start_date.isoformat()
        if end_date is not None:
            params["to"] = end_date.isoformat()

        payload = self._get(
            "historical-price-eod/full",
            params={**params, "symbol": ticker.upper()},
        )
        rows = payload.get("historical", []) if isinstance(payload, dict) else payload
        prices = [
            DailyPrice(
                ticker=ticker.upper(),
                market=market or "US",
                date=date.fromisoformat(row["date"]),
                open=_decimal_or_none(row.get("open")),
                high=_decimal_or_none(row.get("high")),
                low=_decimal_or_none(row.get("low")),
                close=Decimal(str(row["close"])),
                adj_close=_decimal_or_none(row.get("adjClose")),
                volume=_decimal_or_none(row.get("volume")),
                trading_value=None,
                data_source="financialmodelingprep",
            )
            for row in rows
            if row.get("date") and row.get("close") is not None
        ]
        return sorted(prices, key=lambda price: price.date)

    def get_fundamentals(
        self,
        ticker: str,
        market: str | None = None,
    ) -> list[FundamentalsPeriod]:
        symbol = ticker.upper()
        income_rows = self._statement_rows("income-statement", symbol)
        balance_rows = self._statement_rows("balance-sheet-statement", symbol)
        cash_rows = self._statement_rows("cash-flow-statement", symbol)

        balance_by_date = {row.get("date"): row for row in balance_rows}
        cash_by_date = {row.get("date"): row for row in cash_rows}
        periods: list[FundamentalsPeriod] = []
        for income in income_rows:
            period_date = income.get("date")
            if not period_date:
                continue
            balance = balance_by_date.get(period_date, {})
            cash = cash_by_date.get(period_date, {})
            periods.append(
                FundamentalsPeriod(
                    ticker=symbol,
                    market=market or "US",
                    currency=income.get("reportedCurrency") or balance.get("reportedCurrency"),
                    period_end=date.fromisoformat(period_date),
                    period_type=_period_type(income.get("period")),
                    revenue=_decimal_or_none(income.get("revenue")),
                    operating_income=_decimal_or_none(income.get("operatingIncome")),
                    net_income=_decimal_or_none(income.get("netIncome")),
                    total_assets=_decimal_or_none(balance.get("totalAssets")),
                    total_equity=_decimal_or_none(balance.get("totalStockholdersEquity")),
                    total_debt=_decimal_or_none(balance.get("totalDebt")),
                    operating_cash_flow=_decimal_or_none(cash.get("operatingCashFlow")),
                    capex=_decimal_or_none(cash.get("capitalExpenditure")),
                    free_cash_flow=_decimal_or_none(cash.get("freeCashFlow")),
                    shares_outstanding=_decimal_or_none(income.get("weightedAverageShsOutDil")),
                    data_source="financialmodelingprep",
                )
            )
        return sorted(periods, key=lambda period: period.period_end)

    def _statement_rows(self, path: str, symbol: str) -> list[dict[str, Any]]:
        payload = self._get(path, params={"symbol": symbol, "period": "annual", "limit": "5"})
        return payload if isinstance(payload, list) else []

    def _get(self, path: str, params: dict[str, str] | None = None) -> Any:
        if not self.api_key:
            raise RuntimeError("FMP_API_KEY is required to call Financial Modeling Prep.")
        response = self.client.get(
            f"{self.base_url}/{path.lstrip('/')}",
            params={**(params or {}), "apikey": self.api_key},
        )
        response.raise_for_status()
        return response.json()


def _decimal_or_none(value: object) -> Decimal | None:
    if value in (None, ""):
        return None
    return Decimal(str(value))


def _period_type(value: object) -> str:
    return "annual" if str(value or "").upper() == "FY" else str(value or "annual").lower()


def _stable_base_url(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/api/v3"):
        return normalized.removesuffix("/api/v3") + "/stable"
    return normalized
