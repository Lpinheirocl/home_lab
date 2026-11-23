from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class KubernetesResource(Base):
    __tablename__ = "kubernetes_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), index=True)
    resource_type: Mapped[str] = mapped_column(String(40))
    resource_name: Mapped[str] = mapped_column(String(253))
    namespace: Mapped[str] = mapped_column(String(120))
    status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_sync: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
