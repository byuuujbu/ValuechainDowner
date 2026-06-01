from __future__ import annotations

import csv
import uuid
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402

from app.core.config import get_database_url  # noqa: E402
from app.db.schema import assets  # noqa: E402

DEFAULT_ASSETS_CSV = PROJECT_ROOT / "data" / "sample" / "assets.csv"


def asset_id(ticker: str, market: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"ovsa:asset:{market}:{ticker}"))


def load_sample_assets(engine: Engine, path: Path = DEFAULT_ASSETS_CSV) -> int:
    inserted = 0
    with path.open(newline="", encoding="utf-8") as handle, engine.begin() as connection:
        reader = csv.DictReader(handle)
        for row in reader:
            ticker = row["ticker"]
            market = row["market"]
            exists = connection.execute(
                select(assets.c.id).where(assets.c.ticker == ticker, assets.c.market == market)
            ).scalar_one_or_none()
            if exists is not None:
                continue

            connection.execute(
                assets.insert().values(
                    id=asset_id(ticker, market),
                    ticker=ticker,
                    name=row["name"],
                    market=market,
                    country=row.get("country") or None,
                    currency=row.get("currency") or None,
                    asset_type=row["asset_type"],
                    sector=row.get("sector") or None,
                    industry=row.get("industry") or None,
                    is_etf=row["is_etf"].lower() == "true",
                )
            )
            inserted += 1
    return inserted


def main() -> None:
    engine = create_engine(get_database_url())
    inserted = load_sample_assets(engine)
    print(f"Inserted {inserted} sample assets.")


if __name__ == "__main__":
    main()
