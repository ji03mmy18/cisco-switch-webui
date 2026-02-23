"""SSH 連線管理模組，封裝 Netmiko 與 Cisco IOS 的連線操作"""

import threading
from typing import Optional

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
    ReadTimeout,
)


class SSHManager:
    """管理單一持久 SSH 連線到 Cisco 交換器

    使用執行緒鎖保護連線物件，確保多個 API 請求不會同時操作同一連線。
    """

    def __init__(self) -> None:
        self._connection: Optional[ConnectHandler] = None
        self._lock = threading.Lock()
        self._device_info: dict = {}

    def connect(
        self,
        host: str,
        username: str,
        password: str,
        secret: str = "",
    ) -> None:
        """建立 SSH 連線到 Cisco 交換器

        Args:
            host: 交換器 IP 位址或主機名稱
            username: 登入帳號
            password: 登入密碼
            secret: Enable 密碼（選填）

        Raises:
            NetmikoAuthenticationException: 帳號或密碼錯誤
            NetmikoTimeoutException: 連線逾時
            RuntimeError: 其他連線錯誤
        """
        device_params = {
            "device_type": "cisco_ios",
            "host": host,
            "username": username,
            "password": password,
            "secret": secret,
            "timeout": 30,
            "session_timeout": 60,
            "fast_cli": False,
        }

        with self._lock:
            # 若已有連線，先斷開
            if self._connection is not None:
                try:
                    self._connection.disconnect()
                except Exception:
                    pass

            self._connection = ConnectHandler(**device_params)

            # 若有提供 Enable 密碼，進入 privileged 模式
            if secret:
                self._connection.enable()

            self._device_info = {
                "host": host,
                "username": username,
            }

    def disconnect(self) -> None:
        """斷開 SSH 連線並清空連線狀態"""
        with self._lock:
            if self._connection is not None:
                try:
                    self._connection.disconnect()
                except Exception:
                    pass
                finally:
                    self._connection = None
                    self._device_info = {}

    @property
    def is_connected(self) -> bool:
        """檢查目前是否有活躍的 SSH 連線"""
        return self._connection is not None

    def send_command(self, command: str, expect_string: Optional[str] = None) -> str:
        """執行查詢指令（show 類）並回傳輸出

        Args:
            command: 要執行的 CLI 指令
            expect_string: 自訂等待的輸出結尾字串（選填）

        Returns:
            CLI 命令的輸出文字

        Raises:
            RuntimeError: 尚未建立連線
            ReadTimeout: 指令執行逾時
        """
        if self._connection is None:
            raise RuntimeError("尚未建立 SSH 連線，請先登入")

        with self._lock:
            kwargs: dict = {"command_string": command}
            if expect_string:
                kwargs["expect_string"] = expect_string
            return self._connection.send_command(**kwargs)

    def send_config_commands(self, commands: list[str]) -> str:
        """執行設定指令（進入 config mode 後執行）

        Args:
            commands: 要依序執行的設定指令列表

        Returns:
            CLI 命令的輸出文字

        Raises:
            RuntimeError: 尚未建立連線
        """
        if self._connection is None:
            raise RuntimeError("尚未建立 SSH 連線，請先登入")

        with self._lock:
            return self._connection.send_config_set(commands)

    def get_device_info(self) -> dict:
        """取得目前連線的設備基本資訊"""
        return self._device_info.copy()


# 全域單例，在整個應用程式生命週期內共用同一連線
ssh_manager = SSHManager()
