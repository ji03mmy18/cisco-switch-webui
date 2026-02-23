"""Pydantic 資料模型定義"""

from pydantic import BaseModel, Field
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """統一 API 回傳格式"""

    success: bool
    data: Optional[T] = None
    message: str


# ── 連線管理 ────────────────────────────────────────────


class ConnectRequest(BaseModel):
    """SSH 連線請求"""

    host: str = Field(..., description="交換器 IP 位址或主機名稱")
    username: str = Field(..., description="登入帳號")
    password: str = Field(..., description="登入密碼")
    secret: str = Field(default="", description="Enable 密碼（選填）")


class SessionStatus(BaseModel):
    """Session 連線狀態"""

    connected: bool
    has_unsaved_changes: bool
    host: Optional[str] = None
    username: Optional[str] = None


# ── 設備資訊 ────────────────────────────────────────────


class DeviceInfo(BaseModel):
    """設備基本資訊"""

    hostname: str
    model: str
    ios_version: str
    serial_number: str
    uptime: str


class InterfaceStatus(BaseModel):
    """介面狀態資訊"""

    port: str
    name: str
    status: str
    vlan: str
    duplex: str
    speed: str
    type: str
    description: Optional[str] = ""


# ── 介面操作 ────────────────────────────────────────────


class InterfaceConfigRequest(BaseModel):
    """修改介面設定請求"""

    description: Optional[str] = None
    speed: Optional[str] = None
    duplex: Optional[str] = None
    vlan: Optional[int] = None
    mode: Optional[str] = None  # access / trunk


# ── Port 安全設定 ────────────────────────────────────────


class IpsgStatus(BaseModel):
    """IPSG 狀態"""

    interface: str
    enabled: bool


class MacVerifyStatus(BaseModel):
    """MAC Verify 狀態"""

    interface: str
    enabled: bool


class IpMacBinding(BaseModel):
    """IP/MAC 靜態綁定條目"""

    mac_address: str
    vlan_id: int
    ip_address: str
    interface: str
    type: Optional[str] = "static"


class IpMacBindingRequest(BaseModel):
    """新增 IP/MAC 綁定請求"""

    mac_address: str = Field(..., description="MAC 位址（支援 aa:bb:cc:dd:ee:ff 或 aabb.ccdd.eeff 格式）")
    vlan_id: int = Field(..., ge=1, le=4094, description="VLAN ID")
    ip_address: str = Field(..., description="IP 位址（IPv4）")
    interface: str = Field(..., description="介面名稱（如 GigabitEthernet1/0/1）")


class PortSecurityStatus(BaseModel):
    """Port Security 狀態"""

    interface: str
    enabled: bool
    max_mac_count: Optional[int] = None
    current_mac_count: Optional[int] = None
    violation_action: Optional[str] = None
    violation_count: Optional[int] = None


class DhcpSnoopingStatus(BaseModel):
    """DHCP Snooping 全域狀態"""

    enabled: bool
    vlans: list[str]
    trusted_interfaces: list[str]


# ── ARP 檢查 ────────────────────────────────────────────


class ArpBinding(BaseModel):
    """ARP Inspection 綁定條目"""

    ip_address: str
    mac_address: str
    vlan: str
    interface: str


class ArpStatistics(BaseModel):
    """ARP Inspection 統計資訊"""

    vlan: str
    forwarded: int
    dropped: int
    dhcp_drops: int
    arp_probe_drops: int


# ── 網路資訊 ────────────────────────────────────────────


class VlanInfo(BaseModel):
    """VLAN 資訊"""

    vlan_id: int
    name: str
    status: str
    ports: list[str]


class VlanCreateRequest(BaseModel):
    """新增 VLAN 請求"""

    vlan_id: int = Field(..., ge=1, le=4094)
    name: Optional[str] = None


class MacTableEntry(BaseModel):
    """MAC Address Table 條目"""

    vlan: str
    mac_address: str
    mac_type: str
    interface: str


class CdpNeighbor(BaseModel):
    """CDP 鄰居資訊"""

    device_id: str
    local_interface: str
    holdtime: str
    capability: str
    platform: str
    remote_interface: str
    ip_address: Optional[str] = None


class SpanningTreeInfo(BaseModel):
    """Spanning Tree 資訊"""

    vlan: str
    root_id: str
    root_priority: int
    bridge_id: str
    bridge_priority: int
    is_root: bool
    ports: list[dict[str, Any]]
