from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.schemas.discovery import DiscoveredApplication
from app.services.discovery_service import DiscoveryService

router = APIRouter(prefix="/applications", tags=["applications"])
DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/discovered", response_model=list[DiscoveredApplication])
async def list_discovered_applications() -> list[DiscoveredApplication]:
    try:
        return DiscoveryService().discover()
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.post("/discover", response_model=list[DiscoveredApplication])
async def discover_applications() -> list[DiscoveredApplication]:
    try:
        return DiscoveryService().discover()
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(db: DatabaseSession) -> list[Application]:
    result = await db.execute(select(Application).order_by(Application.display_name))
    return list(result.scalars().all())


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(payload: ApplicationCreate, db: DatabaseSession) -> Application:
    application = Application(**payload.model_dump())
    db.add(application)
    try:
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
