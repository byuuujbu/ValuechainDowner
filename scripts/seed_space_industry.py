from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
import sys
import uuid

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = PROJECT_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402

from app.core.config import get_database_url  # noqa: E402
from app.db.schema import industries, value_chain_nodes  # noqa: E402

SPACE_INDUSTRY_ID = "11111111-1111-1111-1111-111111111111"

SPACE_NODES = [
    ("Materials/Parts", "Material and component suppliers for space systems."),
    ("Propulsion/Engines", "Propulsion technology for launch vehicles and spacecraft."),
    ("Launch", "Launch services that place satellites and payloads into orbit."),
    ("Satellite Manufacturing", "Satellite body and payload manufacturing."),
    ("Ground/Communication", "Ground stations and communication infrastructure."),
    ("Space Data", "Satellite data collection, processing, and analytics."),
    ("Government/Commercial Applications", "Space-based defense, commercial, and enterprise use cases."),
]


def deterministic_id(namespace: str, value: str) -> str:
    return str(uuid.uuid5(uuid.UUID(SPACE_INDUSTRY_ID), f"{namespace}:{value}"))


def seed_space_industry(engine: Engine) -> None:
    with engine.begin() as connection:
        existing_by_id = connection.execute(
            select(industries.c.id).where(industries.c.id == SPACE_INDUSTRY_ID)
        ).scalar_one_or_none()
        existing_by_name = connection.execute(
            select(industries.c.id).where(industries.c.name == "Space")
        ).scalar_one_or_none()

        industry_id = existing_by_id or existing_by_name or SPACE_INDUSTRY_ID
        if existing_by_id is not None or existing_by_name is not None:
            connection.execute(
                industries.update()
                .where(industries.c.id == industry_id)
                .values(
                    name="Space",
                    description="Reviewed seed industry for OVSA v0.1.",
                    is_active=True,
                )
            )
        else:
            connection.execute(
                industries.insert().values(
                    id=industry_id,
                    name="Space",
                    description="Reviewed seed industry for OVSA v0.1.",
                    is_active=True,
                )
            )

        for order, (node_name, description) in enumerate(SPACE_NODES, start=1):
            node_exists = connection.execute(
                select(value_chain_nodes.c.id).where(
                    value_chain_nodes.c.industry_id == industry_id,
                    value_chain_nodes.c.node_name == node_name,
                )
            ).scalar_one_or_none()

            if node_exists is None:
                connection.execute(
                    value_chain_nodes.insert().values(
                        id=deterministic_id("space-node", node_name),
                        industry_id=industry_id,
                        node_name=node_name,
                        node_description=description,
                        node_order=order,
                        created_by="system",
                        review_status="reviewed",
                    )
                )


def main(argv: Iterable[str] | None = None) -> None:
    _ = argv
    engine = create_engine(get_database_url())
    seed_space_industry(engine)


if __name__ == "__main__":
    main()
