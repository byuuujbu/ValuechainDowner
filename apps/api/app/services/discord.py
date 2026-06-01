from __future__ import annotations

from app.api.routes import screening_results


def preview_discord_asset_diagnosis(ticker: str) -> str:
    rows = screening_results()["items"]
    row = next((item for item in rows if item["ticker"] == ticker), None)
    if row is None:
        return f"{ticker} diagnosis data not found"
    return (
        f"{ticker} diagnosis complete\n"
        f"status: {row['status']}\n"
        f"total_score: {row['total_score']}\n"
        f"quality: {row['quality_score']} | trend: {row['trend_score']} | "
        f"risk: {row['risk_score']} | valuation: {row['valuation_score']}\n"
        f"reason: {row['reason']}\n"
        "Final judgment and order execution remain user responsibility."
    )
