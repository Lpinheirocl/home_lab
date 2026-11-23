from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Home Server Manager API"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://hsm:hsm@localhost:5432/home_server_manager"
    kubernetes_enabled: bool = False
    kubernetes_in_cluster: bool = True
    public_host: str = "raspberrypi"
    public_http_port: int = 32618
    host_proc_root: str = "/host/proc"
    host_root: str = "/host/root"
    prometheus_url: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="HSM_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
