from datetime import datetime

from pydantic import BaseModel, Field


class PodResponse(BaseModel):
    name: str
    namespace: str
    status: str
    ready: int
    total: int
    restarts: int
    node: str | None = None
    created_at: datetime | None = None
    reason: str | None = None
    restartable: bool = False


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
    network_received_bytes: int = 0
    network_transmitted_bytes: int = 0
    temperature_celsius: float | None = None


class NamespaceResponse(BaseModel):
    name: str
    status: str


class DeploymentResponse(BaseModel):
    name: str
    namespace: str
    replicas: int
    ready_replicas: int
    available_replicas: int


class ServiceResponse(BaseModel):
    name: str
    namespace: str
    type: str
    cluster_ip: str | None = None
    ports: list[str]


class IngressResponse(BaseModel):
    name: str
    namespace: str
    hosts: list[str]
    addresses: list[str]


class EventResponse(BaseModel):
    namespace: str
    name: str
    reason: str | None = None
    message: str
    event_type: str | None = None
    created_at: datetime | None = None


class WorkloadMetricResponse(BaseModel):
    namespace: str
    pod: str
    cpu: str
    memory: str


class ScaleRequest(BaseModel):
    replicas: int = Field(ge=0, le=20)


class ApplicationStatus(BaseModel):
    id: int
    name: str
    display_name: str
    namespace: str | None = None
    status: str
    ready_replicas: int = 0
    replicas: int = 0


class DashboardResponse(BaseModel):
    cluster_connected: bool
    applications_total: int
    applications_online: int
    applications_offline: int
    pods_running: int
    pods_total: int
    applications: list[ApplicationStatus]
    recent_events: list[EventResponse]


class MetricPoint(BaseModel):
    timestamp: datetime
    value: float


class PrometheusMetricsResponse(BaseModel):
    available: bool
    cpu_history: list[MetricPoint]
    memory_history: list[MetricPoint]
