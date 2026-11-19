from fastapi import APIRouter, HTTPException, status

from app.schemas.cluster import PodResponse, TelemetryResponse
from app.services.cluster_service import ClusterService

router = APIRouter(tags=["cluster"])


@router.get(
    "/pods",
    response_model=list[PodResponse],
)
async def list_pods() -> list[PodResponse]:
    try:
        return ClusterService().list_pods()
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

@router.get(
    "/telemetry",
    response_model=TelemetryResponse,
)
async def get_telemetry() -> TelemetryResponse:
    try:
        return ClusterService().telemetry()
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

