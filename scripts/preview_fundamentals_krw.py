from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.data_providers import SampleCsvDataProvider  # noqa: E402
from app.services.currency import convert_fundamentals_to_krw_millions  # noqa: E402

DEFAULT_USD_KRW_RATE = Decimal("1350")


def main() -> None:
    provider = SampleCsvDataProvider()
    for ticker in ("RKLB", "LMT", "NOC", "BA"):
        fundamentals = provider.get_fundamentals(ticker)[0]
        converted = convert_fundamentals_to_krw_millions(
            fundamentals,
            usd_krw_rate=DEFAULT_USD_KRW_RATE,
        )
        print(
            f"{ticker}: revenue={converted.revenue} 백만원, "
            f"free_cash_flow={converted.free_cash_flow} 백만원 "
            f"(USD/KRW={converted.fx_rate})"
        )


if __name__ == "__main__":
    main()
