from datetime import datetime

from pydantic import BaseModel


class PodResponse(BaseModel):
    name: str
    namespace: str
    status: str
    ready: int
    total: int
    restarts: int
    node: str | None = None
    created_at: datetime | None = None


class DiskResponse(BaseModel):
    device: str
    mountpoint: str
    percent: float
    used_bytes: int
    total_bytes: int


class TelemetryResponse(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_bytes: int
    memory_total_bytes: int
    disks: list[DiskResponse]
