from __future__ import annotations

from datetime import date

from app.data_providers.interfaces import AssetProfile
from app.data_providers.sample_csv import SampleCsvDataProvider
from app.scoring.metrics import calculate_raw_metrics
from app.scoring.models import ScoreResult, SubScoreResult
from app.scoring.percentile import percentile_score, weighted_average

QUALITY_WEIGHTS = {
    "roic": 0.30,
    "fcf_conversion": 0.25,
    "earnings_stability": 0.25,
    "operating_margin": 0.20,
}

TREND_WEIGHTS = {
    "six_month_return": 0.35,
    "momentum_12m_ex_1m": 0.35,
    "relative_strength": 0.30,
}

RISK_WEIGHTS = {
    "mdd_1y": 0.40,
    "downside_volatility": 0.35,
    "avg_trading_value": 0.25,
}

VALUATION_WEIGHTS = {
    "fcf_yield": 0.25,
    "ev_ebitda": 0.20,
    "sector_relative_valuation": 0.20,
    "per": 0.20,
    "psr": 0.15,
}

TOTAL_WEIGHTS = {
    "quality": 0.30,
    "trend": 0.25,
    "risk": 0.15,
    "valuation": 0.30,
}

REVERSE_SCORE_METRICS = {"mdd_1y", "downside_volatility", "ev_ebitda", "per", "psr", "sector_relative_valuation"}


class CommonStockScoringEngine:
    def __init__(self, provider: SampleCsvDataProvider) -> None:
        self.provider = provider

    def score_universe(self, as_of: date | None = None) -> dict[str, ScoreResult]:
        common_stocks = [
            asset for asset in self.provider.list_assets() if asset.asset_type == "common_stock"
        ]
        raw_metrics = {
            asset.ticker: calculate_raw_metrics(
                self.provider.get_daily_prices(asset.ticker, end_date=as_of, market=asset.market),
                self.provider.get_fundamentals(asset.ticker, market=asset.market),
            )
            for asset in common_stocks
        }

        metric_scores = self._score_metrics(raw_metrics)
        return {
            asset.ticker: self._build_score_result(asset, raw_metrics[asset.ticker], metric_scores)
            for asset in common_stocks
        }

    def _score_metrics(
        self, raw_metrics: dict[str, dict[str, float | None]]
    ) -> dict[str, dict[str, float | None]]:
        scores: dict[str, dict[str, float | None]] = {ticker: {} for ticker in raw_metrics}
        metric_names = {name for metrics in raw_metrics.values() for name in metrics}
        for metric_name in metric_names:
            peer_values = [metrics[metric_name] for metrics in raw_metrics.values()]
            for ticker, metrics in raw_metrics.items():
                scores[ticker][metric_name] = percentile_score(
                    metrics[metric_name],
                    peer_values,
                    reverse=metric_name in REVERSE_SCORE_METRICS,
                )
        return scores

    def _build_score_result(
        self,
        asset: AssetProfile,
        metrics: dict[str, float | None],
        metric_scores: dict[str, dict[str, float | None]],
    ) -> ScoreResult:
        scores = metric_scores[asset.ticker]
        quality = self._sub_score(scores, QUALITY_WEIGHTS)
        trend = self._sub_score(scores, TREND_WEIGHTS)
        risk = self._sub_score(scores, RISK_WEIGHTS)
        valuation = self._sub_score(scores, VALUATION_WEIGHTS)
        valuation = self._apply_valuation_cap(quality, valuation)
        total = round(
            quality.score * TOTAL_WEIGHTS["quality"]
            + trend.score * TOTAL_WEIGHTS["trend"]
            + risk.score * TOTAL_WEIGHTS["risk"]
            + valuation.score * TOTAL_WEIGHTS["valuation"],
            4,
        )
        confidence = self._score_confidence(metrics)
        latest_price = self.provider.get_daily_prices(asset.ticker, market=asset.market)[-1]

        return ScoreResult(
            ticker=asset.ticker,
            market=asset.market,
            date=latest_price.date,
            metrics=metrics,
            quality=quality,
            trend=trend,
            risk=risk,
            valuation=valuation,
            total_score=total,
            score_confidence=confidence,
            logs=self._logs(asset, metrics, quality, trend, risk, valuation, total, confidence),
        )

    def _sub_score(
        self,
        metric_scores: dict[str, float | None],
        weights: dict[str, float],
    ) -> SubScoreResult:
        components = {key: metric_scores.get(key) for key in weights}
        return SubScoreResult(
            score=weighted_average(components, weights),
            components=components,
            weights=weights,
        )

    def _apply_valuation_cap(
        self, quality: SubScoreResult, valuation: SubScoreResult
    ) -> SubScoreResult:
        if quality.score >= 50:
            return valuation
        capped = min(valuation.score, 60.0)
        return SubScoreResult(score=capped, components=valuation.components, weights=valuation.weights)

    def _score_confidence(self, metrics: dict[str, float | None]) -> float:
        required = [
            "roic",
            "fcf_conversion",
            "operating_margin",
            "six_month_return",
            "momentum_12m_ex_1m",
            "mdd_1y",
            "downside_volatility",
            "avg_trading_value",
            "fcf_yield",
            "ev_ebitda",
            "per",
            "psr",
        ]
        present = sum(1 for key in required if metrics.get(key) is not None)
        return round(present / len(required) * 100, 4)

    def _logs(
        self,
        asset: AssetProfile,
        metrics: dict[str, float | None],
        quality: SubScoreResult,
        trend: SubScoreResult,
        risk: SubScoreResult,
        valuation: SubScoreResult,
        total: float,
        confidence: float,
    ) -> list[dict[str, object]]:
        return [
            {
                "score_type": "total",
                "ticker": asset.ticker,
                "input_metrics_json": metrics,
                "peer_group_json": {"strategy": "sample_common_stock_universe"},
                "percentile_result_json": {
                    "quality": quality.components,
                    "trend": trend.components,
                    "risk": risk.components,
                    "valuation": valuation.components,
                },
                "weighting_json": TOTAL_WEIGHTS,
                "calculation_log_text": (
                    f"quality {quality.score} * 30% + trend {trend.score} * 25% + "
                    f"risk {risk.score} * 15% + valuation {valuation.score} * 30% = {total}"
                ),
                "score_confidence": confidence,
            }
        ]
