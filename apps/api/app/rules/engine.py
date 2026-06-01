from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.data_providers.interfaces import DailyPrice
from app.scoring.models import ScoreResult


@dataclass(frozen=True)
class RuleEventDraft:
    rule_key: str
    action_taken: str
    message: str
    trigger_value: dict[str, float | str]


@dataclass(frozen=True)
class CandidateDecision:
    ticker: str
    status: str
    reason: str
    events: list[RuleEventDraft]


class RuleEngine:
    def evaluate(
        self,
        score: ScoreResult,
        prices: list[DailyPrice],
        *,
        market: str,
        as_of: date | None = None,
    ) -> CandidateDecision:
        events = self._price_events(prices, market=market, as_of=as_of)
        score_reasons = self._score_reasons(score)

        exclude_event = next((event for event in events if event.action_taken == "exclude"), None)
        if exclude_event is not None:
            return CandidateDecision(score.ticker, "exclude", exclude_event.message, events)

        watch_event = next((event for event in events if event.action_taken == "watch"), None)
        if watch_event is not None:
            return CandidateDecision(score.ticker, "watch", watch_event.message, events)

        if score_reasons:
            return CandidateDecision(score.ticker, "watch", "; ".join(score_reasons), events)

        return CandidateDecision(score.ticker, "candidate", "score and structural rules passed", events)

    def _score_reasons(self, score: ScoreResult) -> list[str]:
        reasons: list[str] = []
        if score.total_score < 75:
            reasons.append("total_score_below_75")
        if score.quality.score < 65:
            reasons.append("quality_score_below_65")
        if score.trend.score < 65:
            reasons.append("trend_score_below_65")
        if score.risk.score < 60:
            reasons.append("risk_score_below_60")
        if score.valuation.score < 40:
            reasons.append("valuation_score_below_40")
        if score.score_confidence < 70:
            reasons.append("score_confidence_below_70")
        return reasons

    def _price_events(
        self,
        prices: list[DailyPrice],
        *,
        market: str,
        as_of: date | None,
    ) -> list[RuleEventDraft]:
        relevant_prices = [price for price in prices if as_of is None or price.date <= as_of]
        if len(relevant_prices) < 2:
            return []

        events: list[RuleEventDraft] = []
        five_day_return = period_return(relevant_prices, 5)
        twenty_day_return = period_return(relevant_prices, 20)
        one_day_return = period_return(relevant_prices, 1)

        if five_day_return is not None and five_day_return >= 0.25:
            events.append(
                RuleEventDraft(
                    "surge_5d_25",
                    "exclude",
                    "recent_5_trading_days_return_at_least_25_percent",
                    {"return": round(five_day_return, 6)},
                )
            )
        if twenty_day_return is not None and twenty_day_return >= 0.50:
            events.append(
                RuleEventDraft(
                    "surge_20d_50",
                    "exclude",
                    "recent_20_trading_days_return_at_least_50_percent",
                    {"return": round(twenty_day_return, 6)},
                )
            )
        if one_day_return is not None and one_day_return >= 0.10:
            events.append(
                RuleEventDraft(
                    "surge_1d_10",
                    "exclude",
                    "single_day_return_at_least_10_percent",
                    {"return": round(one_day_return, 6)},
                )
            )
        if market == "US" and one_day_return is not None and abs(one_day_return) >= 0.15:
            events.append(
                RuleEventDraft(
                    "us_one_day_abs_15",
                    "watch",
                    "us_stock_single_day_absolute_return_at_least_15_percent",
                    {"return": round(one_day_return, 6)},
                )
            )
        return events


def period_return(prices: list[DailyPrice], days: int) -> float | None:
    if len(prices) <= days:
        return None
    start = float(prices[-days - 1].close)
    end = float(prices[-1].close)
    if start == 0:
        return None
    return end / start - 1
