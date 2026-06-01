from fastapi import FastAPI

from app.api import router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="OVSA MVP API for sample screening, rules, value-chain maps, journals, and backtests.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ovsa-api"}


app.include_router(router)
