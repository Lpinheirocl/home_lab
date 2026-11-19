import os
import shutil
import time

from app.kubernetes.client import build_api_clients
from app.schemas.cluster import PodResponse, TelemetryResponse


class ClusterService:
    """Consultas somente leitura do cluster e do host que executa a API."""

    def list_pods(self) -> list[PodResponse]:
        core_api, _, _ = build_api_clients()
        result: list[PodResponse] = []
        for pod in core_api.list_pod_for_all_namespaces().items:
            statuses = pod.status.container_statuses or []
            ready = sum(1 for container in statuses if container.ready)
            restarts = sum(
                container.restart_count or 0 for container in statuses
            )
            result.append(
                PodResponse(
                    name=pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    status=pod.status.phase or "Unknown",
                    ready=ready,
                    total=len(statuses),
                    restarts=restarts,
                    node=pod.spec.node_name,
                    created_at=pod.metadata.creation_timestamp,
                )
            )
        return sorted(result, key=lambda pod: (pod.namespace, pod.name))

    def telemetry(self) -> TelemetryResponse:
        memory = self._memory()
        disk = shutil.disk_usage("/")
        total_memory = memory[0]
        used_memory = total_memory - memory[1] - memory[2]
        memory_percent = round(used_memory / total_memory * 100, 1) if total_memory else 0
        return TelemetryResponse(
            cpu_percent=self._cpu_percent(),
            memory_percent=memory_percent,
            memory_used_bytes=used_memory,
            memory_total_bytes=total_memory,
            disk_percent=round(disk.used / disk.total * 100, 1),
            disk_used_bytes=disk.used,
            disk_total_bytes=disk.total,
        )

    @staticmethod
    def _memory() -> tuple[int, int, int]:
        values: dict[str, int] = {}
        with open("/proc/meminfo", encoding="utf-8") as meminfo:
            for line in meminfo:
                key, value = line.split(":", 1)
                values[key] = int(value.strip().split()[0]) * 1024
        return (
            values.get("MemTotal", 0),
            values.get("MemFree", 0),
            values.get("Buffers", 0) + values.get("Cached", 0),
        )

    @staticmethod
    def _cpu_percent() -> float:
        first = ClusterService._cpu_times()
        time.sleep(0.1)
        second = ClusterService._cpu_times()
        total_delta = second[0] - first[0]
        idle_delta = second[1] - first[1]
        if total_delta <= 0:
            return 0
        return round((1 - idle_delta / total_delta) * 100, 1)

    @staticmethod
    def _cpu_times() -> tuple[int, int]:
        with open("/proc/stat", encoding="utf-8") as proc_stat:
            values = proc_stat.readline().split()[1:]
        numbers = [int(value) for value in values]
        idle = numbers[3] + (numbers[4] if len(numbers) > 4 else 0)
        return sum(numbers), idle
