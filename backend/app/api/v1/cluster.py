from fastapi import APIRouter, HTTPException, Query, status
from fastapi.concurrency import run_in_threadpool
from kubernetes.client.exceptions import ApiException

from app.schemas.cluster import (
    DeploymentResponse, EventResponse, IngressResponse, NamespaceResponse,
    PodResponse, ServiceResponse, TelemetryResponse, WorkloadMetricResponse,
    PrometheusMetricsResponse,
)
from app.services.prometheus_service import PrometheusService
from app.services.cluster_service import ClusterService

router = APIRouter(tags=["cluster"])


def _cluster_error(error: Exception) -> HTTPException:
    code = error.status if isinstance(error, ApiException) and error.status else 503
    return HTTPException(status_code=code, detail=str(error))


@router.get("/monitoring/metrics", response_model=PrometheusMetricsResponse)
async def prometheus_metrics() -> PrometheusMetricsResponse:
    return await run_in_threadpool(PrometheusService().history)


@router.get("/namespaces", response_model=list[NamespaceResponse])
async def list_namespaces() -> list[NamespaceResponse]:
    try:
        return ClusterService().list_namespaces()
    except (RuntimeError, ApiException) as error:
        raise _cluster_error(error) from error


@router.get("/kubernetes/deployments", response_model=list[DeploymentResponse])
async def list_deployments() -> list[DeploymentResponse]:
    try:
        return ClusterService().list_deployments()
    except (RuntimeError, ApiException) as error:
        raise _cluster_error(error) from error


@router.get("/kubernetes/services", response_model=list[ServiceResponse])
async def list_services() -> list[ServiceResponse]:
    try:
        return ClusterService().list_services()
    except (RuntimeError, ApiException) as error:
        raise _cluster_error(error) from error


@router.get("/kubernetes/ingresses", response_model=list[IngressResponse])
async def list_ingresses() -> list[IngressResponse]:
    try:
        return ClusterService().list_ingresses()
    except (RuntimeError, ApiException) as error:
        raise _cluster_error(error) from error


@router.get("/kubernetes/events", response_model=list[EventResponse])
async def list_events(limit: int = Query(default=30, ge=1, le=100)) -> list[EventResponse]:
    try:
        return ClusterService().list_events(limit)
    except (RuntimeError, ApiException) as error:
        raise _cluster_error(error) from error


@router.get("/monitoring/workloads", response_model=list[WorkloadMetricResponse])
async def list_workload_metrics() -> list[WorkloadMetricResponse]:
    try:
        return ClusterService().list_workload_metrics()
    except (RuntimeError, ApiException) as error:
        raise _cluster_error(error) from error


@router.get(
    "/pods",
    response_model=list[PodResponse],
)
async def list_pods() -> list[PodResponse]:
    try:
        return ClusterService().list_pods()
    except (RuntimeError, ApiException) as error:
        raise _cluster_error(error) from error


@router.get("/pods/{namespace}/{pod_name}/logs")
async def pod_logs(
    namespace: str,
    pod_name: str,
    tail_lines: int = Query(default=200, ge=1, le=1000),
) -> dict[str, str]:
    try:
        return {"pod": pod_name, "logs": ClusterService().pod_logs(namespace, pod_name, tail_lines)}
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except (RuntimeError, ApiException) as error:
        raise _cluster_error(error) from error


@router.post("/pods/{namespace}/{pod_name}/restart", status_code=status.HTTP_202_ACCEPTED)
async def restart_pod(namespace: str, pod_name: str) -> dict[str, str]:
    try:
        deployment = ClusterService().restart_pod_workload(namespace, pod_name)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except (RuntimeError, ApiException) as error:
        raise _cluster_error(error) from error
    return {"status": "accepted", "message": f"Reinício do Deployment {deployment} solicitado"}

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

