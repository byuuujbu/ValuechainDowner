from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="OVSA Phase 1 API skeleton. No scoring or rule engine here yet.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ovsa-api"}
