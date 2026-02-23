"""設備資訊 API

提供設備基本資訊與所有介面狀態查詢。
"""

from fastapi import APIRouter

from models.schemas import ApiResponse, DeviceInfo, InterfaceStatus
from services.command_parser import parse_command
from services.ssh_manager import ssh_manager

router = APIRouter()


@router.get("/info", response_model=ApiResponse[DeviceInfo])
async def get_device_info():
    """取得交換器基本資訊（型號、IOS 版本、Uptime、序號）"""
    try:
        raw = ssh_manager.send_command("show version")
        parsed = parse_command("show version", raw)

        if not parsed:
            return ApiResponse(success=False, data=None, message="無法解析設備資訊")

        entry = parsed[0]
        info = DeviceInfo(
            hostname=entry.get("HOSTNAME", ""),
            model=entry.get("HARDWARE", [""])[0] if entry.get("HARDWARE") else "",
            ios_version=entry.get("VERSION", ""),
            serial_number=entry.get("SERIAL", [""])[0] if entry.get("SERIAL") else "",
            uptime=entry.get("UPTIME", ""),
        )
        return ApiResponse(success=True, data=info, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")


@router.get("/interfaces", response_model=ApiResponse[list[InterfaceStatus]])
async def get_interfaces():
    """取得所有介面狀態（供視覺化面板使用）"""
    try:
        raw = ssh_manager.send_command("show interfaces status")
        parsed = parse_command("show interfaces status", raw)

        interfaces = [
            InterfaceStatus(
                port=entry.get("PORT", ""),
                name=entry.get("NAME", ""),
                status=entry.get("STATUS", ""),
                vlan=entry.get("VLAN", ""),
                duplex=entry.get("DUPLEX", ""),
                speed=entry.get("SPEED", ""),
                type=entry.get("TYPE", ""),
                description=entry.get("NAME", ""),
            )
            for entry in parsed
        ]
        return ApiResponse(success=True, data=interfaces, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")


@router.get("/interfaces/{interface_id:path}", response_model=ApiResponse[InterfaceStatus])
async def get_interface(interface_id: str):
    """取得單一介面的詳細狀態

    Args:
        interface_id: 介面名稱（如 GigabitEthernet1/0/1）
    """
    try:
        raw = ssh_manager.send_command(f"show interfaces {interface_id} status")
        parsed = parse_command("show interfaces status", raw)

        if not parsed:
            return ApiResponse(success=False, data=None, message=f"找不到介面：{interface_id}")

        entry = parsed[0]
        interface = InterfaceStatus(
            port=entry.get("PORT", ""),
            name=entry.get("NAME", ""),
            status=entry.get("STATUS", ""),
            vlan=entry.get("VLAN", ""),
            duplex=entry.get("DUPLEX", ""),
            speed=entry.get("SPEED", ""),
            type=entry.get("TYPE", ""),
            description=entry.get("NAME", ""),
        )
        return ApiResponse(success=True, data=interface, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")
