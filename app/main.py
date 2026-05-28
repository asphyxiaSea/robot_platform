from fastapi import FastAPI

from app.api.v1.workflow import router as workflow_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "env": settings.env}


app.include_router(workflow_router, prefix="/api/v1")
