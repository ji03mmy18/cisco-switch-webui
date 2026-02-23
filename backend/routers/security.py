"""Port 安全設定 API

處理 IPSG、MAC Verify、IP/MAC 靜態綁定、Port Security 與 DHCP Snooping 狀態查詢。
"""

from fastapi import APIRouter

from models.schemas import (
    ApiResponse,
    DhcpSnoopingStatus,
    IpMacBinding,
    IpMacBindingRequest,
    IpsgStatus,
    MacVerifyStatus,
    PortSecurityStatus,
)
from services.command_parser import parse_command
from services.config_tracker import config_tracker
from services.ssh_manager import ssh_manager

router = APIRouter()


# ── IPSG ──────────────────────────────────────────────


@router.get("/ipsg", response_model=ApiResponse[list[IpsgStatus]])
async def get_ipsg_status():
    """取得所有 Port 的 IPSG 啟用狀態"""
    # TODO: 實作 show ip verify source 解析
    return ApiResponse(success=False, data=None, message="尚未實作")


@router.put("/ipsg/{interface:path}", response_model=ApiResponse[None])
async def set_ipsg(interface: str, enabled: bool):
    """設定指定 Port 的 IPSG 開關

    前置條件：該 Port 所屬 VLAN 必須已啟用 DHCP Snooping。
    """
    # TODO: 實作 ip verify source / no ip verify source
    return ApiResponse(success=False, data=None, message="尚未實作")


# ── MAC Verify ────────────────────────────────────────


@router.get("/mac-verify", response_model=ApiResponse[list[MacVerifyStatus]])
async def get_mac_verify_status():
    """取得所有 Port 的 MAC Verify 啟用狀態"""
    # TODO: 實作解析
    return ApiResponse(success=False, data=None, message="尚未實作")


@router.put("/mac-verify/{interface:path}", response_model=ApiResponse[None])
async def set_mac_verify(interface: str, enabled: bool):
    """設定指定 Port 的 MAC Verify 開關

    前置條件：DHCP Snooping 與 Port Security 均必須已啟用。
    """
    # TODO: 實作 ip verify source port-security / no ip verify source
    return ApiResponse(success=False, data=None, message="尚未實作")


# ── IP/MAC 靜態綁定 ──────────────────────────────────


@router.get("/bindings", response_model=ApiResponse[list[IpMacBinding]])
async def get_bindings():
    """取得所有 IP/MAC 靜態綁定條目"""
    try:
        raw = ssh_manager.send_command("show ip source binding")
        parsed = parse_command("show ip source binding", raw)

        bindings = [
            IpMacBinding(
                mac_address=entry.get("MAC", ""),
                vlan_id=int(entry.get("VLAN", 0)),
                ip_address=entry.get("IP", ""),
                interface=entry.get("INTERFACE", ""),
                type=entry.get("TYPE", "static"),
            )
            for entry in parsed
        ]
        return ApiResponse(success=True, data=bindings, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")


@router.post("/bindings", response_model=ApiResponse[None])
async def add_binding(request: IpMacBindingRequest):
    """新增 IP/MAC 靜態綁定"""
    try:
        cmd = (
            f"ip source binding {request.mac_address} "
            f"vlan {request.vlan_id} "
            f"{request.ip_address} "
            f"interface {request.interface}"
        )
        ssh_manager.send_config_commands([cmd])
        config_tracker.mark_changed()
        return ApiResponse(success=True, data=None, message="綁定新增成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"新增失敗：{e}")


@router.delete("/bindings/{binding_id}", response_model=ApiResponse[None])
async def delete_binding(binding_id: str):
    """刪除 IP/MAC 靜態綁定

    binding_id 格式：{mac}_{vlan}_{ip}（例如 aabb.ccdd.eeff_10_192.168.1.100）
    """
    # TODO: 解析 binding_id 並執行 no ip source binding 指令
    return ApiResponse(success=False, data=None, message="尚未實作")


# ── Port Security ──────────────────────────────────────


@router.get("/port-security", response_model=ApiResponse[list[PortSecurityStatus]])
async def get_port_security():
    """取得所有 Port Security 設定狀態"""
    try:
        raw = ssh_manager.send_command("show port-security")
        parsed = parse_command("show port-security", raw)

        ports = [
            PortSecurityStatus(
                interface=entry.get("INTERFACE", ""),
                enabled=entry.get("PORT_SECURITY", "").lower() == "enabled",
                max_mac_count=int(entry.get("MAX_MAC_ADD", 0)) if entry.get("MAX_MAC_ADD") else None,
                current_mac_count=int(entry.get("CURR_MAC_ADD", 0)) if entry.get("CURR_MAC_ADD") else None,
                violation_action=entry.get("SECURITY_ACTION", ""),
                violation_count=int(entry.get("SECURITY_VIOLATION", 0)) if entry.get("SECURITY_VIOLATION") else None,
            )
            for entry in parsed
        ]
        return ApiResponse(success=True, data=ports, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")


# ── DHCP Snooping ──────────────────────────────────────


@router.get("/dhcp-snooping", response_model=ApiResponse[DhcpSnoopingStatus])
async def get_dhcp_snooping():
    """取得 DHCP Snooping 全域啟用狀態與相關設定"""
    # TODO: 實作 show ip dhcp snooping 解析
    return ApiResponse(success=False, data=None, message="尚未實作")
