import json
import time
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from app.core.config import get_settings
from app.schemas.cluster import MetricPoint, PrometheusMetricsResponse


class PrometheusService:
    def history(self) -> PrometheusMetricsResponse:
        base_url = get_settings().prometheus_url.rstrip("/")
        if not base_url:
            return PrometheusMetricsResponse(available=False, cpu_history=[], memory_history=[])
        end = int(time.time())
        start = end - 3600
        try:
            cpu = self._query(base_url, '100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])))', start, end)
            memory = self._query(base_url, '100 * (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)', start, end)
        except (URLError, TimeoutError, ValueError, KeyError):
            return PrometheusMetricsResponse(available=False, cpu_history=[], memory_history=[])
        return PrometheusMetricsResponse(available=bool(cpu or memory), cpu_history=cpu, memory_history=memory)

    @staticmethod
    def _query(base_url: str, expression: str, start: int, end: int) -> list[MetricPoint]:
        query = urlencode({"query": expression, "start": start, "end": end, "step": 60})
        with urlopen(f"{base_url}/api/v1/query_range?{query}", timeout=3) as response:
            payload = json.load(response)
        result = payload["data"]["result"]
        if not result:
            return []
        return [MetricPoint(timestamp=stamp, value=float(value))
                for stamp, value in result[0]["values"]]
