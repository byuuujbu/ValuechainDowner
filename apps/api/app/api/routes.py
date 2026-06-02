from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.data_providers import SampleCsvDataProvider, data_provider_status
from app.rules import RuleEngine
from app.scoring import CommonStockScoringEngine
from app.services.asset_backdata import get_asset_backdata
from app.services.backtest import run_sample_backtest
from app.services.journal import JOURNAL_REQUIREMENTS, WATCHLIST
from app.services.live_data_diagnostics import fmp_ticker_diagnostics
from app.services.space_map import INDUSTRIES, SPACE_MAP

router = APIRouter()


@router.get("/data-providers/status")
def data_providers_status() -> dict[str, object]:
    return data_provider_status()


@router.get("/data-providers/fmp/{ticker}/diagnostics")
def fmp_diagnostics(ticker: str) -> dict[str, object]:
    return fmp_ticker_diagnostics(ticker)


@router.get("/screening/results")
def screening_results() -> dict[str, object]:
    provider = SampleCsvDataProvider()
    scores = CommonStockScoringEngine(provider).score_universe()
    engine = RuleEngine()
    rows = []
    for score in scores.values():
        decision = engine.evaluate(
            score,
            provider.get_daily_prices(score.ticker, market=score.market),
            market=score.market,
        )
        rows.append(
            {
                "ticker": score.ticker,
                "market": score.market,
                "status": decision.status,
                "reason": decision.reason,
                "total_score": score.total_score,
                "quality_score": score.quality.score,
                "trend_score": score.trend.score,
                "risk_score": score.risk.score,
                "valuation_score": score.valuation.score,
                "score_confidence": score.score_confidence,
            }
        )
    return {"items": rows}


@router.get("/assets/{ticker}/backdata")
def asset_backdata(ticker: str) -> dict[str, object]:
    try:
        return get_asset_backdata(ticker)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/industries")
def industries() -> dict[str, object]:
    return {"items": INDUSTRIES}


@router.get("/industries/space/value-chain")
def space_value_chain() -> dict[str, object]:
    return SPACE_MAP


@router.get("/watchlist")
def watchlist() -> dict[str, object]:
    return {"items": WATCHLIST}


@router.get("/journals/requirements")
def journal_requirements() -> dict[str, object]:
    return {"items": JOURNAL_REQUIREMENTS}


@router.post("/backtests/run")
def backtest_run() -> dict[str, object]:
    return run_sample_backtest()
