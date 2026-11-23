import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.services.cluster_service import ClusterService

app = FastAPI(title="Home Server Manager API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws/dashboard")
async def dashboard_updates(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            try:
                pods = ClusterService().list_pods()
                telemetry = ClusterService().telemetry()
                await websocket.send_json({
                    "type": "dashboard_update",
                    "pods_running": sum(pod.status == "Running" for pod in pods),
                    "pods_total": len(pods),
                    "telemetry": telemetry.model_dump(mode="json"),
                })
            except Exception as error:
                await websocket.send_json({"type": "error", "detail": str(error)})
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        return
