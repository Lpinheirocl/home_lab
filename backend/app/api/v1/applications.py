from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from kubernetes.client.exceptions import ApiException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.application import Application
from app.models.app_event import AppEvent
from app.models.kubernetes_resource import KubernetesResource
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.schemas.discovery import DiscoveredApplication
from app.schemas.cluster import ScaleRequest
from app.services.discovery_service import DiscoveryService
from app.services.cluster_service import ClusterService

router = APIRouter(prefix="/applications", tags=["applications"])
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/discovered", response_model=list[DiscoveredApplication])
async def list_discovered_applications(db: DatabaseSession) -> list[DiscoveredApplication]:
    try:
        discovered = DiscoveryService().discover()
        registered = set((await db.execute(select(Application.namespace, Application.name))).all())
        return [item for item in discovered if (item.namespace, item.name) not in registered]
    except (RuntimeError, ApiException) as error:
        code = error.status if isinstance(error, ApiException) and error.status else status.HTTP_503_SERVICE_UNAVAILABLE
        raise HTTPException(status_code=code, detail=str(error)) from error


@router.post("/discover", response_model=list[DiscoveredApplication])
async def discover_applications(db: DatabaseSession) -> list[DiscoveredApplication]:
    try:
        discovered = DiscoveryService().discover()
        registered = set((await db.execute(select(Application.namespace, Application.name))).all())
        return [item for item in discovered if (item.namespace, item.name) not in registered]
    except (RuntimeError, ApiException) as error:
        code = error.status if isinstance(error, ApiException) and error.status else status.HTTP_503_SERVICE_UNAVAILABLE
        raise HTTPException(status_code=code, detail=str(error)) from error


async def _get_deployment_application(
    application_id: int, db: AsyncSession
) -> tuple[Application, KubernetesResource]:
    application = await db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada")
    result = await db.execute(select(KubernetesResource).where(
        KubernetesResource.application_id == application_id,
        KubernetesResource.resource_type == "Deployment",
    ).limit(1))
    deployment = result.scalar_one_or_none()
    if deployment is None:
        if not application.namespace:
            raise HTTPException(status_code=409, detail="Aplicação sem Deployment Kubernetes associado")
        try:
            discovered = DiscoveryService().discover()
        except (RuntimeError, ApiException) as error:
            code = error.status if isinstance(error, ApiException) and error.status else 503
            raise HTTPException(status_code=code, detail=str(error)) from error
        candidate = next((item for item in discovered
                          if item.namespace == application.namespace and item.name == application.name), None)
        if candidate is None:
            raise HTTPException(
                status_code=409,
                detail="Nenhum Deployment com este nome foi encontrado no namespace cadastrado",
            )
        deployment = KubernetesResource(
            application_id=application.id,
            resource_type="Deployment",
            resource_name=candidate.deployment_name,
            namespace=candidate.namespace,
        )
        db.add(deployment)
        db.add_all([KubernetesResource(
            application_id=application.id,
            resource_type="Service",
            resource_name=service_name,
            namespace=candidate.namespace,
        ) for service_name in candidate.services])
        await db.commit()
    return application, deployment


@router.get("/{application_id}/logs")
async def application_logs(
    application_id: int,
    db: DatabaseSession,
    tail_lines: int = Query(default=200, ge=1, le=1000),
) -> dict[str, str]:
    application, deployment = await _get_deployment_application(application_id, db)
    try:
        logs = ClusterService().application_logs(deployment.namespace, deployment.resource_name, tail_lines)
        return {"application": application.display_name, "logs": logs}
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except (ApiException, RuntimeError) as error:
        code = error.status if isinstance(error, ApiException) and error.status else 503
        raise HTTPException(status_code=code, detail=str(error)) from error


@router.post("/{application_id}/restart", status_code=status.HTTP_202_ACCEPTED)
async def restart_application(application_id: int, db: DatabaseSession) -> dict[str, str]:
    application, deployment = await _get_deployment_application(application_id, db)
    try:
        ClusterService().restart_deployment(deployment.namespace, deployment.resource_name)
    except (ApiException, RuntimeError) as error:
        code = error.status if isinstance(error, ApiException) and error.status else 503
        raise HTTPException(status_code=code, detail=str(error)) from error
    db.add(AppEvent(application_id=application.id, event_type="deployment_restart",
                    message=f"Reinício de {application.display_name} solicitado"))
    await db.commit()
    return {"status": "accepted", "message": f"Reinício de {application.display_name} solicitado"}


@router.post("/{application_id}/scale", status_code=status.HTTP_202_ACCEPTED)
async def scale_application(
    application_id: int, payload: ScaleRequest, db: DatabaseSession
) -> dict[str, str]:
    application, deployment = await _get_deployment_application(application_id, db)
    try:
        ClusterService().scale_deployment(deployment.namespace, deployment.resource_name, payload.replicas)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except (ApiException, RuntimeError) as error:
        code = error.status if isinstance(error, ApiException) and error.status else 503
        raise HTTPException(status_code=code, detail=str(error)) from error
    db.add(AppEvent(application_id=application.id, event_type="deployment_scale",
                    message=f"Escala de {application.display_name} solicitada para {payload.replicas} réplicas"))
    await db.commit()
    return {"status": "accepted", "message": f"Escala de {application.display_name} solicitada"}


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(db: DatabaseSession) -> list[Application]:
    result = await db.execute(select(Application).order_by(Application.display_name))
    return list(result.scalars().all())


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(payload: ApplicationCreate, db: DatabaseSession) -> Application:
    application = Application(**payload.model_dump(exclude={"resources"}))
    db.add(application)
    try:
        await db.flush()
        db.add_all([
            KubernetesResource(application_id=application.id, **resource.model_dump())
            for resource in payload.resources
        ])
        await db.commit()
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nome já cadastrado") from error
    await db.refresh(application)
    return application


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: int, db: DatabaseSession) -> Application:
    application = await db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aplicação não encontrada")
    return application


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: int, payload: ApplicationUpdate, db: DatabaseSession
) -> Application:
    application = await db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aplicação não encontrada")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, field, value)
    await db.commit()
    await db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(application_id: int, db: DatabaseSession) -> None:
    application = await db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aplicação não encontrada")

    await db.delete(application)
    await db.commit()
