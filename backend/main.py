"""FastAPI 應用程式入口

Cisco 交換器網頁管理介面後端服務。
啟動指令：uv run uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import arp, auth, device, interfaces, maintenance, network, security

app = FastAPI(
    title="Cisco Switch Web UI",
    description="Cisco WS-C2960X-48TS-L 網頁管理介面 API",
    version="0.1.0",
)

# 允許前端開發伺服器跨域存取
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊所有路由模組
app.include_router(auth.router, prefix="/api", tags=["連線管理"])
app.include_router(device.router, prefix="/api/device", tags=["設備資訊"])
app.include_router(security.router, prefix="/api/security", tags=["Port 安全設定"])
app.include_router(arp.router, prefix="/api/arp", tags=["ARP 檢查"])
app.include_router(network.router, prefix="/api/network", tags=["網路資訊"])
app.include_router(interfaces.router, prefix="/api/interfaces", tags=["介面操作"])
app.include_router(maintenance.router, prefix="/api/maintenance", tags=["維護管理"])


@app.get("/", tags=["健康檢查"])
async def root():
    """健康檢查端點"""
    return {"status": "ok", "message": "Cisco Switch Web UI API 運行中"}
