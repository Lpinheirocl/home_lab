from fastapi import APIRouter

from app.api.v1.applications import router as applications_router
from app.api.v1.cluster import router as cluster_router

api_router = APIRouter()
api_router.include_router(applications_router)
api_router.include_router(cluster_router)


@api_router.get("/health", tags=["system"])
async def api_health() -> dict[str, str]:
    return {"status": "ok", "api": "v1"}
