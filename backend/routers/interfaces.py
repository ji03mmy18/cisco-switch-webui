"""介面操作 API

提供介面開關、速率、雙工、description 與 VLAN 設定。
"""

from fastapi import APIRouter

from models.schemas import ApiResponse, InterfaceConfigRequest
from services.config_tracker import config_tracker
from services.ssh_manager import ssh_manager

router = APIRouter()


@router.put("/{interface_id:path}/shutdown", response_model=ApiResponse[None])
async def shutdown_interface(interface_id: str):
    """關閉介面（需前端二次確認）"""
    try:
        ssh_manager.send_config_commands([
            f"interface {interface_id}",
            "shutdown",
        ])
        config_tracker.mark_changed()
        return ApiResponse(success=True, data=None, message=f"介面 {interface_id} 已關閉")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"操作失敗：{e}")


@router.put("/{interface_id:path}/no-shutdown", response_model=ApiResponse[None])
async def no_shutdown_interface(interface_id: str):
    """開啟介面"""
    try:
        ssh_manager.send_config_commands([
            f"interface {interface_id}",
            "no shutdown",
        ])
        config_tracker.mark_changed()
        return ApiResponse(success=True, data=None, message=f"介面 {interface_id} 已開啟")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"操作失敗：{e}")


@router.put("/{interface_id:path}/config", response_model=ApiResponse[None])
async def configure_interface(interface_id: str, request: InterfaceConfigRequest):
    """修改介面設定（速率、雙工模式、description、VLAN）"""
    try:
        commands = [f"interface {interface_id}"]

        if request.description is not None:
            commands.append(f"description {request.description}")

        if request.speed is not None:
            commands.append(f"speed {request.speed}")

        if request.duplex is not None:
            commands.append(f"duplex {request.duplex}")

        if request.vlan is not None:
            if request.mode == "access":
                commands.append("switchport mode access")
                commands.append(f"switchport access vlan {request.vlan}")
            elif request.mode == "trunk":
                commands.append("switchport mode trunk")
                commands.append(f"switchport trunk allowed vlan add {request.vlan}")

        if len(commands) == 1:
            return ApiResponse(success=False, data=None, message="未提供任何設定項目")

        ssh_manager.send_config_commands(commands)
        config_tracker.mark_changed()
        return ApiResponse(success=True, data=None, message=f"介面 {interface_id} 設定已更新")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"設定失敗：{e}")
