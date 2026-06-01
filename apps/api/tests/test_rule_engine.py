from dataclasses import replace

from app.data_providers import SampleCsvDataProvider
from app.rules import RuleEngine
from app.scoring import CommonStockScoringEngine


def test_rule_engine_returns_candidate_when_all_thresholds_pass() -> None:
    provider = SampleCsvDataProvider()
    score = CommonStockScoringEngine(provider).score_universe()["LMT"]

    decision = RuleEngine().evaluate(score, provider.get_daily_prices("LMT"), market="US")

    assert decision.status == "candidate"


def test_rule_engine_blocks_low_risk_score() -> None:
    provider = SampleCsvDataProvider()
    score = CommonStockScoringEngine(provider).score_universe()["RKLB"]

    decision = RuleEngine().evaluate(score, provider.get_daily_prices("RKLB"), market="US")

    assert decision.status == "watch"
    assert "risk_score_below_60" in decision.reason


def test_rule_engine_excludes_recent_surge() -> None:
    provider = SampleCsvDataProvider()
    prices = provider.get_daily_prices("LMT")
    surged = prices[:-1] + [replace(prices[-1], close=prices[-6].close * 2)]
    score = CommonStockScoringEngine(provider).score_universe()["LMT"]

    decision = RuleEngine().evaluate(score, surged, market="US")

    assert decision.status == "exclude"
    assert decision.events[0].rule_key == "surge_5d_25"
