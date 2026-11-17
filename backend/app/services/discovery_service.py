from app.kubernetes.client import build_api_clients
from app.schemas.discovery import DiscoveredApplication


class DiscoveryService:
    """Descobre workloads sem criar, alterar ou remover recursos no cluster."""

    def discover(self) -> list[DiscoveredApplication]:
        core_api, apps_api, networking_api = build_api_clients()
        service_selectors: list[tuple[str, str, dict[str, str]]] = []
        for service in core_api.list_service_for_all_namespaces().items:
            selector = service.spec.selector or {}
            if selector:
                service_selectors.append((service.metadata.namespace, service.metadata.name, selector))

        ingress_hosts: dict[tuple[str, str], list[str]] = {}
        for ingress in networking_api.list_ingress_for_all_namespaces().items:
            for rule in ingress.spec.rules or []:
                for path in rule.http.paths if rule.http else []:
                    if path.backend.service and path.backend.service.name:
                        key = (ingress.metadata.namespace, path.backend.service.name)
                        ingress_hosts.setdefault(key, []).append(rule.host or "")

        discovered: list[DiscoveredApplication] = []
        for deployment in apps_api.list_deployment_for_all_namespaces().items:
            namespace = deployment.metadata.namespace
            name = deployment.metadata.name
            labels = deployment.spec.template.metadata.labels or {}
            services = [name for service_namespace, name, selector in service_selectors if service_namespace == namespace and all(labels.get(key) == value for key, value in selector.items())]
            hosts = [host for service in services for host in ingress_hosts.get((namespace, service), [])]
            replicas = deployment.spec.replicas or 0
            ready_replicas = deployment.status.ready_replicas or 0
            discovered.append(DiscoveredApplication(name=name, namespace=namespace, display_name=name.replace("-", " ").title(), deployment_name=name, replicas=replicas, ready_replicas=ready_replicas, services=sorted(set(services)), ingress_hosts=sorted(set(hosts))))
        return discovered
