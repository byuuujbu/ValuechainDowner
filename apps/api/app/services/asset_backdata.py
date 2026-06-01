from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal

from app.data_providers import SampleCsvDataProvider
from app.data_providers.interfaces import DailyPrice, FundamentalsPeriod
from app.rules import RuleEngine
from app.scoring import CommonStockScoringEngine
from app.scoring.models import ScoreResult, SubScoreResult


SCORE_LABELS = {
    "quality": "퀄리티",
    "trend": "추세",
    "risk": "위험",
    "valuation": "밸류에이션",
}

METRIC_LABELS = {
    "roic": "투하자본수익률",
    "fcf_conversion": "잉여현금흐름 전환율",
    "earnings_stability": "이익 안정성",
    "operating_margin": "영업이익률",
    "six_month_return": "6개월 수익률",
    "momentum_12m_ex_1m": "12개월 모멘텀",
    "relative_strength": "상대 강도",
    "mdd_1y": "1년 최대낙폭",
    "downside_volatility": "하방 변동성",
    "avg_trading_value": "평균 거래대금",
    "fcf_yield": "FCF 수익률",
    "ev_ebitda": "EV/EBITDA",
    "sector_relative_valuation": "섹터 상대 밸류에이션",
    "per": "PER",
    "psr": "PSR",
}


def get_asset_backdata(ticker: str) -> dict[str, object]:
    provider = SampleCsvDataProvider()
    asset = provider.get_asset(ticker)
    prices = provider.get_daily_prices(asset.ticker, market=asset.market)
    fundamentals = provider.get_fundamentals(asset.ticker, market=asset.market)
    score = CommonStockScoringEngine(provider).score_universe()[asset.ticker]
    decision = RuleEngine().evaluate(score, prices, market=asset.market)

    return {
        "asset": {
            "ticker": asset.ticker,
            "name": asset.name,
            "market": asset.market,
            "country": asset.country,
            "currency": asset.currency,
            "sector": asset.sector,
            "industry": asset.industry,
            "asset_type": asset.asset_type,
        },
        "decision": {
            "status": decision.status,
            "reason": decision.reason,
            "events": [asdict(event) for event in decision.events],
        },
        "score": _score_payload(score),
        "price_summary": _price_summary(prices),
        "fundamentals": [_fundamental_payload(item) for item in fundamentals],
        "source": {
            "provider": "SampleCsvDataProvider",
            "price_file": "data/sample/price_daily_sample.csv",
            "fundamentals_file": "data/sample/fundamentals_sample.csv",
            "assets_file": "data/sample/assets.csv",
            "notice": "현재 값은 샘플 CSV 기반이며 실제 투자 판단용 실데이터가 아닙니다.",
        },
    }


def _score_payload(score: ScoreResult) -> dict[str, object]:
    return {
        "as_of": score.date.isoformat(),
        "total_score": score.total_score,
        "score_confidence": score.score_confidence,
        "dimensions": [
            _subscore_payload("quality", score.quality),
            _subscore_payload("trend", score.trend),
            _subscore_payload("risk", score.risk),
            _subscore_payload("valuation", score.valuation),
        ],
        "raw_metrics": [
            {
                "key": key,
                "label": METRIC_LABELS.get(key, key),
                "value": value,
            }
            for key, value in score.metrics.items()
        ],
        "calculation_logs": score.logs,
    }


def _subscore_payload(key: str, subscore: SubScoreResult) -> dict[str, object]:
    return {
        "key": key,
        "label": SCORE_LABELS[key],
        "score": subscore.score,
        "components": [
            {
                "key": component_key,
                "label": METRIC_LABELS.get(component_key, component_key),
                "score": component_score,
                "weight": subscore.weights[component_key],
            }
            for component_key, component_score in subscore.components.items()
        ],
    }


def _price_summary(prices: list[DailyPrice]) -> dict[str, object]:
    latest = prices[-1]
    first = prices[0]
    high = max(prices, key=lambda item: item.close)
    low = min(prices, key=lambda item: item.close)
    return {
        "rows": len(prices),
        "start_date": first.date.isoformat(),
        "end_date": latest.date.isoformat(),
        "latest_close": _decimal_to_float(latest.close),
        "year_high_close": _decimal_to_float(high.close),
        "year_low_close": _decimal_to_float(low.close),
        "latest_volume": _decimal_to_float(latest.volume),
        "latest_trading_value": _decimal_to_float(latest.trading_value),
        "sample_rows": [_price_payload(item) for item in prices[-5:]],
    }


def _price_payload(price: DailyPrice) -> dict[str, object]:
    return {
        "date": price.date.isoformat(),
        "open": _decimal_to_float(price.open),
        "high": _decimal_to_float(price.high),
        "low": _decimal_to_float(price.low),
        "close": _decimal_to_float(price.close),
        "volume": _decimal_to_float(price.volume),
        "trading_value": _decimal_to_float(price.trading_value),
        "data_source": price.data_source,
    }


def _fundamental_payload(fundamental: FundamentalsPeriod) -> dict[str, object]:
    return {
        "period_end": fundamental.period_end.isoformat(),
        "period_type": fundamental.period_type,
        "currency": fundamental.currency,
        "revenue": _decimal_to_float(fundamental.revenue),
        "operating_income": _decimal_to_float(fundamental.operating_income),
        "net_income": _decimal_to_float(fundamental.net_income),
        "total_assets": _decimal_to_float(fundamental.total_assets),
        "total_equity": _decimal_to_float(fundamental.total_equity),
        "total_debt": _decimal_to_float(fundamental.total_debt),
        "operating_cash_flow": _decimal_to_float(fundamental.operating_cash_flow),
        "capex": _decimal_to_float(fundamental.capex),
        "free_cash_flow": _decimal_to_float(fundamental.free_cash_flow),
        "shares_outstanding": _decimal_to_float(fundamental.shares_outstanding),
        "data_source": fundamental.data_source,
    }


def _decimal_to_float(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None
