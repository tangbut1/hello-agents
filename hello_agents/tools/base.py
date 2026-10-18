"""tools/base.py — 工具的基类。

一个工具 = 名字 + 描述 + 执行函数。
描述是给模型看的"岗位说明书"——模型靠它决定该不该调这个工具。
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional


class Tool:
    """一个可被智能体调用的工具。"""

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable[[str], str],
        parameters: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters or {}  # 预留：以后接 OpenAI function calling

    def run(self, tool_input: str) -> str:
        """执行工具。异常不许炸掉 agent，变成文字错误返回。

        TODO 1（约 4 行）:
            try:
                return str(self.func(tool_input))
            except Exception as e:
                return f"工具执行出错: {e}"
        """
        raise NotImplementedError("TODO 1: 实现 Tool.run")

    def to_prompt(self) -> str:
        """给模型看的清单行，格式: -name: description

        TODO 2（1 行）:
            return f"-{self.name}: {self.description}"
        """
        raise NotImplementedError("TODO 2: 实现 Tool.to_prompt")

    def __repr__(self) -> str:
        return f"Tool({self.name})"
