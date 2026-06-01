from __future__ import annotations

from decimal import Decimal


def run_sample_backtest() -> dict[str, object]:
    return {
        "mode": "sample_structural_check",
        "screening_cadence_days": 3,
        "rebalancing_review_cadence_days": 14,
        "assumptions": {
            "transaction_cost": "0.10%",
            "slippage": "0.05%",
            "data_scope": "sample CSV only",
            "performance_guarantee": False,
        },
        "results": {
            "strategy_return": str(Decimal("0.0842")),
            "mdd": str(Decimal("0.0715")),
            "benchmark": "SPY + QQQ sample blend",
            "downside_defense": "sample check only",
        },
        "notice": "Sample data validates structure only; it does not guarantee performance.",
    }
