"""設定變更追蹤模組

追蹤 running-config 是否有尚未儲存至 startup-config 的變更。
每次執行寫入類指令後，呼叫 mark_changed()；
執行 write memory 後，呼叫 mark_saved()。
"""


class ConfigTracker:
    """追蹤未儲存變更狀態的單例類別"""

    def __init__(self) -> None:
        self._has_unsaved_changes: bool = False

    def mark_changed(self) -> None:
        """標記有未儲存至 startup-config 的變更"""
        self._has_unsaved_changes = True

    def mark_saved(self) -> None:
        """標記設定已成功儲存（執行 write memory 後呼叫）"""
        self._has_unsaved_changes = False

    def reset(self) -> None:
        """重置狀態（登出時呼叫）"""
        self._has_unsaved_changes = False

    @property
    def has_changes(self) -> bool:
        """是否有未儲存的變更"""
        return self._has_unsaved_changes


# 全域單例
config_tracker = ConfigTracker()
