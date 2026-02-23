"""ARP 檢查 API

提供 ARP Inspection 綁定資訊與統計數據查詢。
"""

from fastapi import APIRouter

from models.schemas import ApiResponse, ArpBinding, ArpStatistics
from services.command_parser import parse_command
from services.ssh_manager import ssh_manager

router = APIRouter()


@router.get("/bindings", response_model=ApiResponse[list[ArpBinding]])
async def get_arp_bindings():
    """取得 ARP Inspection 綁定資訊（show ip arp inspection bindings）"""
    try:
        raw = ssh_manager.send_command("show ip arp inspection bindings")
        parsed = parse_command("show ip arp inspection bindings", raw)

        bindings = [
            ArpBinding(
                ip_address=entry.get("IP_ADDRESS", ""),
                mac_address=entry.get("MAC_ADDRESS", ""),
                vlan=entry.get("VLAN", ""),
                interface=entry.get("INTERFACE", ""),
            )
            for entry in parsed
        ]
        return ApiResponse(success=True, data=bindings, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")


@router.get("/statistics", response_model=ApiResponse[list[ArpStatistics]])
async def get_arp_statistics():
    """取得 ARP Inspection 統計數據（show ip arp inspection statistics）"""
    try:
        raw = ssh_manager.send_command("show ip arp inspection statistics")
        parsed = parse_command("show ip arp inspection statistics", raw)

        stats = [
            ArpStatistics(
                vlan=entry.get("VLAN", ""),
                forwarded=int(entry.get("FORWARDED", 0)),
                dropped=int(entry.get("DROPPED", 0)),
                dhcp_drops=int(entry.get("DHCP_DROPS", 0)),
                arp_probe_drops=int(entry.get("ARP_PROBE", 0)),
            )
            for entry in parsed
        ]
        return ApiResponse(success=True, data=stats, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")
