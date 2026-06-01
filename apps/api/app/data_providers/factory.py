from __future__ import annotations

from app.core.config import settings
from app.data_providers.fmp import FinancialModelingPrepProvider
from app.data_providers.sample_csv import DEFAULT_SAMPLE_DIR, SampleCsvDataProvider
from app.data_providers.sec_edgar import SecEdgarClient


def get_configured_provider() -> SampleCsvDataProvider | FinancialModelingPrepProvider:
    mode = settings.data_provider_mode.strip().lower()
    if mode == "fmp":
        return FinancialModelingPrepProvider()
    return SampleCsvDataProvider()


def data_provider_status() -> dict[str, object]:
    mode = settings.data_provider_mode.strip().lower()
    fmp = FinancialModelingPrepProvider()
    sec = SecEdgarClient()
    active_provider = "financialmodelingprep" if mode == "fmp" and fmp.is_configured else "sample_csv"
    notices = []
    if mode == "fmp" and not fmp.is_configured:
        notices.append("FMP_API_KEY is not set. API calls that require FMP will fail until configured.")
    if not sec.is_configured:
        notices.append("SEC_USER_AGENT is not set. SEC EDGAR calls are disabled until configured.")
    return {
        "mode": mode,
        "active_provider": active_provider,
        "sample_available": DEFAULT_SAMPLE_DIR.exists(),
        "fmp_configured": fmp.is_configured,
        "sec_edgar_configured": sec.is_configured,
        "notices": notices,
    }
