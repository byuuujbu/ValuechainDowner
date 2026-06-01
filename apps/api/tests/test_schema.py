from sqlalchemy import create_engine

from app.db.schema import metadata


def test_phase_2_tables_are_declared() -> None:
    expected_tables = {
        "assets",
        "asset_aliases",
        "industries",
        "value_chain_nodes",
        "asset_value_chain_map",
        "price_daily",
        "fundamentals_periodic",
        "calculated_metrics",
        "scores_daily",
        "score_logs",
        "benchmarks",
        "market_interest_daily",
        "news_articles",
        "watchlists",
        "portfolios",
        "positions",
        "trades",
        "trade_journals",
        "rules",
        "rule_events",
        "backtest_runs",
        "backtest_results",
        "ai_explanations",
    }

    assert set(metadata.tables) == expected_tables


def test_schema_can_create_all_tables_in_sqlite() -> None:
    engine = create_engine("sqlite:///:memory:")

    metadata.create_all(engine)

    assert set(metadata.tables) == set(metadata.tables)
