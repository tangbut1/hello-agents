"""内置工具：安全计算器（只允许数字和四则运算）。

这个文件是**工作示例**：你看它怎么用 Tool 的，照着理解即可，不用改。
"""
from __future__ import annotations

import re

from ..base import Tool

# 白名单：只允许数字、空格和四则运算符
_ALLOWED = re.compile(r"^[\d\s+\-*/().]+$")


def calculator_func(expr: str) -> str:
    expr = expr.strip()
    if not _ALLOWED.match(expr):
        return "错误：表达式只允许数字和 + - * / ( )"
    try:
        # 白名单校验后再 eval，没有内置函数可调，安全
        result = eval(expr, {"__builtins__": {}}, {})
        return f"{expr} = {result}"
    except ZeroDivisionError:
        return "错误：除数为 0"
    except Exception as e:
        return f"错误：无法计算（{e}）"


def build_calculator_tool() -> Tool:
    """构造计算器工具。"""
    return Tool(
        name="calculator",
        description="计算器。输入一个四则运算表达式，例如 (15*8+32)。",
        func=calculator_func,
    )
