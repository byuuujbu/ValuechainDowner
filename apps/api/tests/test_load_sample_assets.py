from sqlalchemy import create_engine, func, select

from app.db.schema import assets, metadata
from scripts.load_sample_assets import DEFAULT_ASSETS_CSV, load_sample_assets


def test_load_sample_assets_is_idempotent() -> None:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)

    first_inserted = load_sample_assets(engine, DEFAULT_ASSETS_CSV)
    second_inserted = load_sample_assets(engine, DEFAULT_ASSETS_CSV)

    with engine.connect() as connection:
        asset_count = connection.execute(select(func.count()).select_from(assets)).scalar_one()

    assert first_inserted == 10
    assert second_inserted == 0
    assert asset_count == 10
