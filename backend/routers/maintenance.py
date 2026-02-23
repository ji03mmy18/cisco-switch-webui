"""維護管理 API

提供儲存設定、備份、設定比對、系統日誌與設備重啟功能。
"""

from fastapi import APIRouter

from models.schemas import ApiResponse
from services.config_tracker import config_tracker
from services.ssh_manager import ssh_manager

router = APIRouter()


@router.post("/save", response_model=ApiResponse[None])
async def save_config():
    """儲存設定至 startup-config（write memory）"""
    try:
        output = ssh_manager.send_command("write memory", expect_string=r"\[OK\]|Building configuration")
        config_tracker.mark_saved()
        return ApiResponse(success=True, data=None, message="設定已成功儲存至 startup-config")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"儲存失敗：{e}")


@router.get("/config/running", response_model=ApiResponse[str])
async def get_running_config():
    """取得 running-config 完整內容"""
    try:
        output = ssh_manager.send_command("show running-config")
        return ApiResponse(success=True, data=output, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")


@router.get("/config/startup", response_model=ApiResponse[str])
async def get_startup_config():
    """取得 startup-config 完整內容"""
    try:
        output = ssh_manager.send_command("show startup-config")
        return ApiResponse(success=True, data=output, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")


@router.get("/config/diff", response_model=ApiResponse[str])
async def get_config_diff():
    """比較 running-config 與 startup-config 的差異"""
    try:
        running = ssh_manager.send_command("show running-config")
        startup = ssh_manager.send_command("show startup-config")

        # 逐行比對，標記差異
        running_lines = set(running.splitlines())
        startup_lines = set(startup.splitlines())

        added = [f"+ {line}" for line in running_lines - startup_lines if line.strip()]
        removed = [f"- {line}" for line in startup_lines - running_lines if line.strip()]

        diff = "\n".join(sorted(removed) + sorted(added))
        if not diff:
            diff = "（running-config 與 startup-config 無差異）"

        return ApiResponse(success=True, data=diff, message="比對完成")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"比對失敗：{e}")


@router.get("/logging", response_model=ApiResponse[str])
async def get_logging():
    """取得系統日誌（show logging）"""
    try:
        output = ssh_manager.send_command("show logging")
        return ApiResponse(success=True, data=output, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")


@router.post("/reload", response_model=ApiResponse[None])
async def reload_device():
    """重啟設備（需前端多重確認）

    警告：執行後設備將會重啟，所有連線將中斷。
    """
    try:
        # 送出 reload 指令，並回應確認提示
        ssh_manager.send_command("reload", expect_string=r"confirm|reload")
        ssh_manager.send_command("\n", expect_string=r"#")
        # 重啟後連線將自動中斷
        ssh_manager.disconnect()
        config_tracker.reset()
        return ApiResponse(success=True, data=None, message="設備重啟指令已送出")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        # 重啟時連線中斷是預期行為
        return ApiResponse(success=True, data=None, message="設備重啟指令已送出")
