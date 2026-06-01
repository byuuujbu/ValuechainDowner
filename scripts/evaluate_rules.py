from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from sqlalchemy import create_engine, select  # noqa: E402

from app.core.config import get_database_url  # noqa: E402
from app.data_providers import SampleCsvDataProvider  # noqa: E402
from app.db.schema import assets, scores_daily  # noqa: E402
from app.rules import RuleEngine  # noqa: E402
from app.scoring import CommonStockScoringEngine  # noqa: E402
from app.scoring.persistence import persist_score_results  # noqa: E402


def main() -> None:
    provider = SampleCsvDataProvider()
    scores = CommonStockScoringEngine(provider).score_universe()
    engine = create_engine(get_database_url())
    persist_score_results(engine, scores)
    rule_engine = RuleEngine()

    with engine.begin() as connection:
        asset_ids = {
            row.ticker: row.id for row in connection.execute(select(assets.c.id, assets.c.ticker))
        }
        for score in scores.values():
            prices = provider.get_daily_prices(score.ticker, market=score.market)
            decision = rule_engine.evaluate(score, prices, market=score.market)
            connection.execute(
                scores_daily.update()
                .where(scores_daily.c.asset_id == asset_ids[score.ticker])
                .where(scores_daily.c.date == score.date)
                .values(candidate_status=decision.status, status_reason=decision.reason)
            )
            print(f"{score.ticker}: {decision.status} - {decision.reason}")


if __name__ == "__main__":
    main()
