from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SubScoreResult:
    score: float
    components: dict[str, float | None]
    weights: dict[str, float]


@dataclass(frozen=True)
class ScoreResult:
    ticker: str
    market: str
    date: date
    metrics: dict[str, float | None]
    quality: SubScoreResult
    trend: SubScoreResult
    risk: SubScoreResult
    valuation: SubScoreResult
    total_score: float
    score_confidence: float
    logs: list[dict[str, object]]
