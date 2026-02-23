"""連線管理 API

處理 SSH 連線的建立、斷開與 Session 狀態查詢。
"""

from fastapi import APIRouter
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

from models.schemas import ApiResponse, ConnectRequest, SessionStatus
from services.config_tracker import config_tracker
from services.ssh_manager import ssh_manager

router = APIRouter()


@router.post("/connect", response_model=ApiResponse[SessionStatus])
async def connect(request: ConnectRequest):
    """建立 SSH 連線到 Cisco 交換器"""
    try:
        ssh_manager.connect(
            host=request.host,
            username=request.username,
            password=request.password,
            secret=request.secret,
        )
        config_tracker.reset()

        status = SessionStatus(
            connected=True,
            has_unsaved_changes=False,
            host=request.host,
            username=request.username,
        )
        return ApiResponse(success=True, data=status, message="連線成功")

    except NetmikoAuthenticationException:
        return ApiResponse(
            success=False,
            data=None,
            message="認證失敗：帳號或密碼錯誤，請確認後重試",
        )
    except NetmikoTimeoutException:
        return ApiResponse(
            success=False,
            data=None,
            message="連線逾時：請確認 IP 位址與網路連通性",
        )
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"連線失敗：{e}")


@router.post("/disconnect", response_model=ApiResponse[None])
async def disconnect():
    """斷開 SSH 連線"""
    ssh_manager.disconnect()
    config_tracker.reset()
    return ApiResponse(success=True, data=None, message="已成功登出")


@router.get("/session/status", response_model=ApiResponse[SessionStatus])
async def get_session_status():
    """取得目前 Session 連線狀態與未儲存變更旗標"""
    if not ssh_manager.is_connected:
        status = SessionStatus(connected=False, has_unsaved_changes=False)
        return ApiResponse(success=True, data=status, message="尚未連線")

    device_info = ssh_manager.get_device_info()
    status = SessionStatus(
        connected=True,
        has_unsaved_changes=config_tracker.has_changes,
        host=device_info.get("host"),
        username=device_info.get("username"),
    )
    return ApiResponse(success=True, data=status, message="連線中")
