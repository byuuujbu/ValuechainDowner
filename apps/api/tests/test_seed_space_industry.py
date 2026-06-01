from sqlalchemy import create_engine, func, select

from app.db.schema import industries, metadata, value_chain_nodes
from scripts.seed_space_industry import SPACE_NODES, seed_space_industry


def test_seed_space_industry_is_idempotent() -> None:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)

    seed_space_industry(engine)
    seed_space_industry(engine)

    with engine.connect() as connection:
        industry_count = connection.execute(select(func.count()).select_from(industries)).scalar_one()
        node_count = connection.execute(
            select(func.count()).select_from(value_chain_nodes)
        ).scalar_one()

    assert industry_count == 1
    assert node_count == len(SPACE_NODES)
