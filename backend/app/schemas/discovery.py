from pydantic import BaseModel


class DiscoveredApplication(BaseModel):
    name: str
    namespace: str
    display_name: str
    deployment_name: str
    replicas: int
    ready_replicas: int
    services: list[str]
    ingress_hosts: list[str]
    access_url: str | None = None
    source: str = "kubernetes"
