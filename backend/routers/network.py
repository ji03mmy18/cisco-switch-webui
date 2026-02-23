"""網路資訊 API

提供 VLAN 管理、MAC Address Table、CDP 鄰居與 Spanning Tree 查詢。
"""

from fastapi import APIRouter

from models.schemas import (
    ApiResponse,
    CdpNeighbor,
    MacTableEntry,
    SpanningTreeInfo,
    VlanCreateRequest,
    VlanInfo,
)
from services.command_parser import parse_command
from services.config_tracker import config_tracker
from services.ssh_manager import ssh_manager

router = APIRouter()


# ── VLAN 管理 ──────────────────────────────────────────


@router.get("/vlans", response_model=ApiResponse[list[VlanInfo]])
async def get_vlans():
    """取得所有 VLAN 列表（show vlan brief）"""
    try:
        raw = ssh_manager.send_command("show vlan brief")
        parsed = parse_command("show vlan brief", raw)

        vlans = [
            VlanInfo(
                vlan_id=int(entry.get("VLAN_ID", 0)),
                name=entry.get("NAME", ""),
                status=entry.get("STATUS", ""),
                ports=entry.get("INTERFACES", []),
            )
            for entry in parsed
            if entry.get("VLAN_ID", "").isdigit()
        ]
        return ApiResponse(success=True, data=vlans, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")


@router.post("/vlans", response_model=ApiResponse[None])
async def create_vlan(request: VlanCreateRequest):
    """新增 VLAN"""
    try:
        commands = [f"vlan {request.vlan_id}"]
        if request.name:
            commands.append(f"name {request.name}")
        ssh_manager.send_config_commands(commands)
        config_tracker.mark_changed()
        return ApiResponse(success=True, data=None, message=f"VLAN {request.vlan_id} 建立成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"建立失敗：{e}")


@router.delete("/vlans/{vlan_id}", response_model=ApiResponse[None])
async def delete_vlan(vlan_id: int):
    """刪除 VLAN（危險操作，需前端二次確認）"""
    try:
        ssh_manager.send_config_commands([f"no vlan {vlan_id}"])
        config_tracker.mark_changed()
        return ApiResponse(success=True, data=None, message=f"VLAN {vlan_id} 已刪除")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"刪除失敗：{e}")


# ── MAC Address Table ──────────────────────────────────


@router.get("/mac-table", response_model=ApiResponse[list[MacTableEntry]])
async def get_mac_table():
    """取得 MAC Address Table（show mac address-table）"""
    try:
        raw = ssh_manager.send_command("show mac address-table")
        parsed = parse_command("show mac address-table", raw)

        entries = [
            MacTableEntry(
                vlan=entry.get("DESTINATION_ADDRESS", ""),
                mac_address=entry.get("DESTINATION_ADDRESS", ""),
                mac_type=entry.get("TYPE", ""),
                interface=entry.get("DESTINATION_PORT", [""])[0] if isinstance(entry.get("DESTINATION_PORT"), list) else entry.get("DESTINATION_PORT", ""),
            )
            for entry in parsed
        ]
        return ApiResponse(success=True, data=entries, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")


# ── CDP 鄰居 ───────────────────────────────────────────


@router.get("/cdp-neighbors", response_model=ApiResponse[list[CdpNeighbor]])
async def get_cdp_neighbors():
    """取得 CDP 鄰居設備資訊（show cdp neighbors detail）"""
    try:
        raw = ssh_manager.send_command("show cdp neighbors detail")
        parsed = parse_command("show cdp neighbors detail", raw)

        neighbors = [
            CdpNeighbor(
                device_id=entry.get("DEVICE_ID", ""),
                local_interface=entry.get("LOCAL_INTERFACE", ""),
                holdtime=entry.get("HOLDTIME", ""),
                capability=entry.get("CAPABILITIES", ""),
                platform=entry.get("PLATFORM", ""),
                remote_interface=entry.get("REMOTE_PORT", ""),
                ip_address=entry.get("MANAGEMENT_IP", None),
            )
            for entry in parsed
        ]
        return ApiResponse(success=True, data=neighbors, message="查詢成功")

    except RuntimeError as e:
        return ApiResponse(success=False, data=None, message=str(e))
    except Exception as e:
        return ApiResponse(success=False, data=None, message=f"查詢失敗：{e}")


# ── Spanning Tree ──────────────────────────────────────


@router.get("/spanning-tree", response_model=ApiResponse[list[SpanningTreeInfo]])
async def get_spanning_tree():
    """取得 Spanning Tree 狀態（show spanning-tree）"""
    # TODO: 實作 STP 解析（結構較複雜，需特殊處理）
    return ApiResponse(success=False, data=None, message="尚未實作")
