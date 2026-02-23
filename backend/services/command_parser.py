"""CLI 輸出解析模組

優先使用 ntc-templates 的 TextFSM template 解析 Cisco IOS 命令輸出。
若無對應 template，則使用正則表達式手動解析。
"""

from typing import Any

from ntc_templates.parse import parse_output


def parse_command(command: str, raw_output: str) -> list[dict[str, Any]]:
    """使用 ntc-templates 解析 Cisco IOS 命令輸出

    Args:
        command: 執行的 CLI 指令（如 "show interfaces status"）
        raw_output: CLI 輸出的原始文字

    Returns:
        解析後的資料列表，每個元素為一個字典

    Raises:
        Exception: 若無對應 template 或解析失敗
    """
    result = parse_output(
        platform="cisco_ios",
        command=command,
        data=raw_output,
    )
    return result


def parse_command_safe(command: str, raw_output: str) -> list[dict[str, Any]]:
    """安全版本的命令解析，失敗時回傳空列表而非拋出例外

    Args:
        command: 執行的 CLI 指令
        raw_output: CLI 輸出的原始文字

    Returns:
        解析後的資料列表，解析失敗時回傳空列表
    """
    try:
        return parse_command(command, raw_output)
    except Exception:
        return []
