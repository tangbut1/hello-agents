"""tools/registry.py — 工具注册表：智能体的工具箱。"""
from __future__ import annotations

from typing import Dict, List, Optional

from .base import Tool


class ToolRegistry:
    """名字 -> Tool 的登记册。"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """注册一个工具。重名就覆盖，并提醒。"""
        if tool.name in self._tools:
            print(f"警告：工具'{tool.name}'已存在，将被覆盖。")
        self._tools[tool.name] = tool
        print(f"工具'{tool.name}'已注册。")

    def get(self, name: str) -> Optional[Tool]:
        """按名取工具；没有返回 None（不炸）。"""
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())

    def describe(self) -> str:
        """生成给模型看的工具清单（每行一个工具）。"""
        return "\n".join(t.to_prompt() for t in self._tools.values())
