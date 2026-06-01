from __future__ import annotations

import uuid
from collections.abc import Iterable
from pathlib import Path
import sys

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
    ("소재/부품", "우주 산업에 쓰이는 핵심 소재와 부품 공급 단계"),
    ("추진체/엔진", "발사체와 우주 시스템의 추진 기술 단계"),
    ("발사체", "위성 및 화물을 궤도에 올리는 발사 서비스 단계"),
    ("위성 제조", "위성 본체와 탑재체 제조 단계"),
    ("지상국/통신", "위성 관제, 지상국, 통신 인프라 단계"),
    ("우주 데이터", "위성 데이터 수집, 처리, 분석 단계"),
    ("국방/상업/탐사 응용", "우주 기반 국방, 상업, 탐사 응용 단계"),
]


def deterministic_id(namespace: str, value: str) -> str:
    return str(uuid.uuid5(uuid.UUID(SPACE_INDUSTRY_ID), f"{namespace}:{value}"))


def seed_space_industry(engine: Engine) -> None:
    with engine.begin() as connection:
        existing = connection.execute(
            select(industries.c.id).where(industries.c.name == "우주")
        ).scalar_one_or_none()

        industry_id = existing or SPACE_INDUSTRY_ID
        if existing is None:
            connection.execute(
                industries.insert().values(
                    id=industry_id,
                    name="우주",
                    description="OVSA v0.1에서 우선 상세 구현하는 산업",
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
