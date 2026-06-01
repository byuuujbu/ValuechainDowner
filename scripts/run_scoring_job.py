from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from sqlalchemy import create_engine  # noqa: E402

from app.core.config import get_database_url  # noqa: E402
from app.data_providers import SampleCsvDataProvider  # noqa: E402
from app.scoring import CommonStockScoringEngine  # noqa: E402
from app.scoring.persistence import persist_score_results  # noqa: E402


def main() -> None:
    provider = SampleCsvDataProvider()
    scoring_engine = CommonStockScoringEngine(provider)
    results = scoring_engine.score_universe()
    persist_score_results(create_engine(get_database_url()), results)

    for result in results.values():
        print(
            f"{result.ticker}: total={result.total_score}, "
            f"quality={result.quality.score}, trend={result.trend.score}, "
            f"risk={result.risk.score}, valuation={result.valuation.score}, "
            f"confidence={result.score_confidence}"
        )


if __name__ == "__main__":
    main()
