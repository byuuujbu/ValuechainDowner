from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from app.db.schema import assets, calculated_metrics, score_logs, scores_daily
from app.scoring.models import ScoreResult


def persist_score_results(engine: Engine, results: dict[str, ScoreResult]) -> None:
    with engine.begin() as connection:
        asset_ids = {
            row.ticker: row.id
            for row in connection.execute(select(assets.c.id, assets.c.ticker)).all()
        }

        for result in results.values():
            asset_id = asset_ids[result.ticker]
            metric_values = {
                "id": deterministic_id("calculated_metrics", result.ticker, result.date.isoformat()),
                "asset_id": asset_id,
                "date": result.date,
                **result.metrics,
            }
            score_values = {
                "id": deterministic_id("scores_daily", result.ticker, result.date.isoformat()),
                "asset_id": asset_id,
                "date": result.date,
                "quality_score": result.quality.score,
                "trend_score": result.trend.score,
                "risk_score": result.risk.score,
                "valuation_score": result.valuation.score,
                "total_score": result.total_score,
                "score_confidence": result.score_confidence,
            }

            connection.execute(
                insert(calculated_metrics)
                .values(metric_values)
                .on_conflict_do_update(
                    index_elements=["asset_id", "date"],
                    set_={key: value for key, value in metric_values.items() if key != "id"},
                )
            )
            connection.execute(
                insert(scores_daily)
                .values(score_values)
                .on_conflict_do_update(
                    index_elements=["asset_id", "date"],
                    set_={key: value for key, value in score_values.items() if key != "id"},
                )
            )
            for index, log in enumerate(result.logs):
                connection.execute(
                    insert(score_logs)
                    .values(
                        id=deterministic_id(
                            "score_logs",
                            result.ticker,
                            result.date.isoformat(),
                            str(index),
                        ),
                        asset_id=asset_id,
                        date=result.date,
                        score_type=str(log["score_type"]),
                        input_metrics_json=log["input_metrics_json"],
                        peer_group_json=log["peer_group_json"],
                        percentile_result_json=log["percentile_result_json"],
                        weighting_json=log["weighting_json"],
                        calculation_log_text=str(log["calculation_log_text"]),
                    )
                    .on_conflict_do_update(
                        index_elements=["id"],
                        set_={
                            "input_metrics_json": log["input_metrics_json"],
                            "peer_group_json": log["peer_group_json"],
                            "percentile_result_json": log["percentile_result_json"],
                            "weighting_json": log["weighting_json"],
                            "calculation_log_text": str(log["calculation_log_text"]),
                        },
                    )
                )


def deterministic_id(*parts: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "ovsa:" + ":".join(parts)))
