import os
import shutil
import time
import glob
from datetime import datetime, timezone

from app.core.config import get_settings
from app.kubernetes.client import build_api_clients
from app.schemas.cluster import (
    DeploymentResponse,
    DiskResponse,
    EventResponse,
    IngressResponse,
    NamespaceResponse,
    PodResponse,
    ServiceResponse,
    TelemetryResponse,
    WorkloadMetricResponse,
)


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

    def list_namespaces(self) -> list[NamespaceResponse]:
        core_api, _, _ = build_api_clients()
        return [NamespaceResponse(name=item.metadata.name, status=item.status.phase or "Unknown")
                for item in core_api.list_namespace().items]

    def list_deployments(self) -> list[DeploymentResponse]:
        _, apps_api, _ = build_api_clients()
        return [DeploymentResponse(
            name=item.metadata.name,
            namespace=item.metadata.namespace,
            replicas=item.spec.replicas or 0,
            ready_replicas=item.status.ready_replicas or 0,
            available_replicas=item.status.available_replicas or 0,
        ) for item in apps_api.list_deployment_for_all_namespaces().items]

    def list_services(self) -> list[ServiceResponse]:
        core_api, _, _ = build_api_clients()
        return [ServiceResponse(
            name=item.metadata.name,
            namespace=item.metadata.namespace,
            type=item.spec.type or "ClusterIP",
            cluster_ip=item.spec.cluster_ip,
            ports=[f"{port.port}/{port.protocol or 'TCP'}" for port in item.spec.ports or []],
        ) for item in core_api.list_service_for_all_namespaces().items]

    def list_ingresses(self) -> list[IngressResponse]:
        _, _, networking_api = build_api_clients()
        return [IngressResponse(
            name=item.metadata.name,
            namespace=item.metadata.namespace,
            hosts=sorted({rule.host for rule in item.spec.rules or [] if rule.host}),
            addresses=[address.ip for address in (item.status.load_balancer.ingress or [])
                       if address.ip] if item.status and item.status.load_balancer else [],
        ) for item in networking_api.list_ingress_for_all_namespaces().items]

    def list_events(self, limit: int = 30) -> list[EventResponse]:
        core_api, _, _ = build_api_clients()
        events = core_api.list_event_for_all_namespaces().items
        def event_time(item):
            return item.last_timestamp or item.event_time or item.metadata.creation_timestamp
        events.sort(key=lambda item: event_time(item) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return [EventResponse(
            namespace=item.metadata.namespace or "default",
            name=item.involved_object.name if item.involved_object else item.metadata.name,
            reason=item.reason,
            message=item.message or "",
            event_type=item.type,
            created_at=event_time(item),
        ) for item in events[:limit]]

    def list_workload_metrics(self) -> list[WorkloadMetricResponse]:
        from kubernetes import client

        build_api_clients()  # Load the configured in-cluster or local Kubernetes credentials.
        api = client.CustomObjectsApi()
        result = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "pods")
        return [WorkloadMetricResponse(
            namespace=item["metadata"]["namespace"],
            pod=item["metadata"]["name"],
            cpu=self._sum_cpu(container.get("usage", {}).get("cpu", "0")
                              for container in item.get("containers", [])),
            memory=self._sum_memory(container.get("usage", {}).get("memory", "0")
                                    for container in item.get("containers", [])),
        ) for item in result.get("items", [])]

    @staticmethod
    def _sum_cpu(values) -> str:
        total_millicores = 0.0
        for value in values:
            quantity = str(value)
            if quantity.endswith("n"):
                total_millicores += float(quantity[:-1]) / 1_000_000
            elif quantity.endswith("u"):
                total_millicores += float(quantity[:-1]) / 1_000
            elif quantity.endswith("m"):
                total_millicores += float(quantity[:-1])
            else:
                total_millicores += float(quantity) * 1000
        return f"{round(total_millicores)}m"

    @staticmethod
    def _sum_memory(values) -> str:
        factors = {"Ki": 1024, "Mi": 1024**2, "Gi": 1024**3,
                   "Ti": 1024**4, "K": 1000, "M": 1000**2,
                   "G": 1000**3, "T": 1000**4}
        total_bytes = 0
        for value in values:
            quantity = str(value)
            suffix = next((suffix for suffix in factors if quantity.endswith(suffix)), "")
            number = quantity[:-len(suffix)] if suffix else quantity
            total_bytes += int(float(number) * factors.get(suffix, 1))
        return f"{total_bytes} B"

    def application_logs(self, namespace: str, deployment_name: str, tail_lines: int = 200) -> str:
        core_api, apps_api, _ = build_api_clients()
        deployment = apps_api.read_namespaced_deployment(deployment_name, namespace)
        selector = deployment.spec.selector.match_labels or {}
        label_selector = ",".join(f"{key}={value}" for key, value in selector.items())
        if not label_selector:
            raise ValueError("Deployment sem selector de Pods")
        pods = core_api.list_namespaced_pod(namespace, label_selector=label_selector).items
        if not pods:
            return "Nenhum Pod encontrado para este Deployment."
        pod = sorted(pods, key=lambda item: item.metadata.name)[0]
        containers = pod.spec.containers or []
        if not containers:
            return "O Pod não possui containers."
        return core_api.read_namespaced_pod_log(
            pod.metadata.name, namespace, container=containers[0].name,
            tail_lines=max(1, min(tail_lines, 1000)), timestamps=True,
        )

    def restart_deployment(self, namespace: str, deployment_name: str) -> None:
        from datetime import datetime, timezone
        _, apps_api, _ = build_api_clients()
        apps_api.patch_namespaced_deployment(
            deployment_name, namespace,
            {"spec": {"template": {"metadata": {"annotations": {
                "kubectl.kubernetes.io/restartedAt": datetime.now(timezone.utc).isoformat()
            }}}}},
        )

    def scale_deployment(self, namespace: str, deployment_name: str, replicas: int) -> None:
        if replicas < 0 or replicas > 20:
            raise ValueError("O número de réplicas deve estar entre 0 e 20")
        _, apps_api, _ = build_api_clients()
        apps_api.patch_namespaced_deployment(deployment_name, namespace, {"spec": {"replicas": replicas}})

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
            network_received_bytes=self._network_bytes(settings.host_proc_root, 0),
            network_transmitted_bytes=self._network_bytes(settings.host_proc_root, 8),
            temperature_celsius=self._temperature(settings.host_root),
        )

    @staticmethod
    def _network_bytes(proc_root: str, column: int) -> int:
        total = 0
        with open(f"{proc_root}/1/net/dev", encoding="utf-8") as network:
            for line in network.readlines()[2:]:
                interface, _, counters = line.partition(":")
                if not counters or interface.strip() == "lo":
                    continue
                values = counters.split()
                if len(values) > column:
                    total += int(values[column])
        return total

    @staticmethod
    def _temperature(host_root: str) -> float | None:
        for path in glob.glob(f"{host_root}/sys/class/thermal/thermal_zone*/temp"):
            try:
                with open(path, encoding="utf-8") as temperature:
                    value = float(temperature.read().strip())
            except (OSError, ValueError):
                continue
            return round(value / 1000 if value > 1000 else value, 1)
        return None

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
            "squashfs",
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
