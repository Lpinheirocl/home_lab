import os
import shutil
import time

from app.core.config import get_settings
from app.kubernetes.client import build_api_clients
from app.schemas.cluster import DiskResponse, PodResponse, TelemetryResponse


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
        settings = get_settings()
        proc_root = (
            settings.host_proc_root
            if os.path.isfile(f"{settings.host_proc_root}/meminfo")
            else "/proc"
        )
        memory = self._memory(proc_root)
        disks = self._disks(settings.host_proc_root, settings.host_root)
        total_memory = memory[0]
        used_memory = total_memory - memory[1] - memory[2]
        memory_percent = round(used_memory / total_memory * 100, 1) if total_memory else 0
        return TelemetryResponse(
            cpu_percent=self._cpu_percent(proc_root),
            memory_percent=memory_percent,
            memory_used_bytes=used_memory,
            memory_total_bytes=total_memory,
            disks=disks,
        )

    @staticmethod
    def _disks(host_proc_root: str, host_root: str) -> list[DiskResponse]:
        disks: list[DiskResponse] = []
        seen_mountpoints: set[str] = set()
        # /proc/mounts is namespace-aware and reflects the reader's namespace.
        # Read PID 1's mount table from the host proc mount instead.
        with open(f"{host_proc_root}/1/mounts", encoding="utf-8") as mounts:
            partitions = [line.split()[:3] for line in mounts if len(line.split()) >= 3]
        pseudo_filesystems = {
            "autofs",
            "cgroup",
            "cgroup2",
            "devpts",
            "mqueue",
            "proc",
            "procfs",
            "sysfs",
            "tmpfs",
        }
        for device, raw_mountpoint, filesystem in partitions:
            mountpoint = raw_mountpoint.replace("\\040", " ").replace("\\011", "\t")
            if filesystem in pseudo_filesystems or not device.startswith("/dev/"):
                continue
            if mountpoint.startswith("/var/lib/kubelet/"):
                continue
            if mountpoint in seen_mountpoints:
                continue
            host_path = os.path.join(host_root, mountpoint.lstrip("/"))
            try:
                usage = shutil.disk_usage(host_path)
            except OSError:
                continue
            if usage.total == 0:
                continue
            seen_mountpoints.add(mountpoint)
            disks.append(
                DiskResponse(
                    device=device or "filesystem",
                    mountpoint=mountpoint,
                    percent=round(usage.used / usage.total * 100, 1),
                    used_bytes=usage.used,
                    total_bytes=usage.total,
                )
            )
        return sorted(disks, key=lambda disk: disk.mountpoint)

    @staticmethod
    def _memory(proc_root: str) -> tuple[int, int, int]:
        values: dict[str, int] = {}
        with open(f"{proc_root}/meminfo", encoding="utf-8") as meminfo:
            for line in meminfo:
                key, value = line.split(":", 1)
                values[key] = int(value.strip().split()[0]) * 1024
        return (
            values.get("MemTotal", 0),
            values.get("MemFree", 0),
            values.get("Buffers", 0) + values.get("Cached", 0),
        )

    @staticmethod
    def _cpu_percent(proc_root: str) -> float:
        first = ClusterService._cpu_times(proc_root)
        time.sleep(0.1)
        second = ClusterService._cpu_times(proc_root)
        total_delta = second[0] - first[0]
        idle_delta = second[1] - first[1]
        if total_delta <= 0:
            return 0
        return round((1 - idle_delta / total_delta) * 100, 1)

    @staticmethod
    def _cpu_times(proc_root: str) -> tuple[int, int]:
        with open(f"{proc_root}/stat", encoding="utf-8") as proc_stat:
            values = proc_stat.readline().split()[1:]
        numbers = [int(value) for value in values]
        idle = numbers[3] + (numbers[4] if len(numbers) > 4 else 0)
        return sum(numbers), idle
