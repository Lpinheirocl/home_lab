from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from kubernetes.client.exceptions import ApiException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.application import Application
from app.models.app_event import AppEvent
from app.schemas.cluster import ApplicationStatus, DashboardResponse, EventResponse
from app.services.cluster_service import ClusterService
from app.services.discovery_service import DiscoveryService

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(db: AsyncSession = Depends(get_db)) -> DashboardResponse:
    applications = list((await db.execute(select(Application).order_by(Application.display_name))).scalars())
    try:
        discovered = DiscoveryService().discover()
        pods = ClusterService().list_pods()
        events = ClusterService().list_events(10)
    except (RuntimeError, ApiException) as error:
        raise HTTPException(status_code=503, detail=f"Não foi possível consultar o cluster: {error}") from error

    discovered_by_key = {(item.namespace, item.name): item for item in discovered}
    statuses: list[ApplicationStatus] = []
    for application in applications:
        resource = discovered_by_key.get((application.namespace, application.name))
        if resource is None:
            state, ready, desired = "unknown", 0, 0
        else:
            ready, desired = resource.ready_replicas, resource.replicas
            state = "offline" if ready == 0 else "online" if ready >= desired else "degraded"
        statuses.append(ApplicationStatus(
            id=application.id,
            name=application.name,
            display_name=application.display_name,
            namespace=application.namespace,
            status=state,
            ready_replicas=ready,
            replicas=desired,
        ))

    app_events = list((await db.execute(
        select(AppEvent).order_by(desc(AppEvent.created_at)).limit(10)
    )).scalars())
    recent_events = events + [
        EventResponse(
            namespace="home-server-manager",
            name=f"application:{event.application_id or 'platform'}",
            reason=event.event_type,
            message=event.message,
            event_type="Normal",
            created_at=event.created_at,
        ) for event in app_events
    ]
    recent_events.sort(
        key=lambda item: item.created_at or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return DashboardResponse(
        cluster_connected=True,
        applications_total=len(applications),
        applications_online=sum(item.status == "online" for item in statuses),
        applications_offline=sum(item.status in {"offline", "degraded"} for item in statuses),
        pods_running=sum(item.status == "Running" for item in pods),
        pods_total=len(pods),
        applications=statuses,
        recent_events=recent_events[:10],
    )
