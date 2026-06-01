from datetime import date

from app.data_providers import SampleCsvDataProvider
from app.scoring import CommonStockScoringEngine
from app.scoring.engine import TOTAL_WEIGHTS
from app.scoring.models import SubScoreResult


def test_scoring_engine_scores_common_stocks_only() -> None:
    results = CommonStockScoringEngine(SampleCsvDataProvider()).score_universe()

    assert set(results) == {"RKLB", "LMT", "NOC", "BA"}


def test_total_score_uses_required_weights() -> None:
    result = CommonStockScoringEngine(SampleCsvDataProvider()).score_universe()["LMT"]

    expected = round(
        result.quality.score * TOTAL_WEIGHTS["quality"]
        + result.trend.score * TOTAL_WEIGHTS["trend"]
        + result.risk.score * TOTAL_WEIGHTS["risk"]
        + result.valuation.score * TOTAL_WEIGHTS["valuation"],
        4,
    )

    assert result.total_score == expected


def test_lower_risk_metrics_score_higher() -> None:
    results = CommonStockScoringEngine(SampleCsvDataProvider()).score_universe()

    best_mdd_ticker = min(results, key=lambda ticker: results[ticker].metrics["mdd_1y"] or 999)
    best_mdd_score_ticker = max(
        results, key=lambda ticker: results[ticker].risk.components["mdd_1y"] or -1
    )

    assert best_mdd_ticker == best_mdd_score_ticker


def test_na_metrics_are_ignored_in_weighted_subscore() -> None:
    results = CommonStockScoringEngine(SampleCsvDataProvider()).score_universe()

    rklb = results["RKLB"]

    assert rklb.valuation.components["per"] is None
    assert rklb.valuation.score >= 0
    assert rklb.score_confidence < 100


def test_valuation_score_is_capped_when_quality_is_low() -> None:
    engine = CommonStockScoringEngine(SampleCsvDataProvider())
    quality = SubScoreResult(score=45.0, components={}, weights={})
    valuation = SubScoreResult(score=88.0, components={}, weights={})

    capped = engine._apply_valuation_cap(quality, valuation)

    assert capped.score == 60.0


def test_score_result_contains_score_log_payload() -> None:
    result = CommonStockScoringEngine(SampleCsvDataProvider()).score_universe()["NOC"]

    assert result.date == date(2026, 5, 29)
    assert result.logs[0]["score_type"] == "total"
    assert "calculation_log_text" in result.logs[0]
    assert result.logs[0]["weighting_json"] == TOTAL_WEIGHTS
