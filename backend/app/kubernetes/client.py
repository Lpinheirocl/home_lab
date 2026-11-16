from kubernetes import client, config

from app.core.config import get_settings


def build_api_clients() -> tuple[client.CoreV1Api, client.AppsV1Api, client.NetworkingV1Api]:
    """Cria clientes Kubernetes; não executa consultas por si só."""
    settings = get_settings()
    if not settings.kubernetes_enabled:
        raise RuntimeError("A integração Kubernetes está desativada")
    if settings.kubernetes_in_cluster:
        config.load_incluster_config()
    else:
        config.load_kube_config()
    return client.CoreV1Api(), client.AppsV1Api(), client.NetworkingV1Api()
