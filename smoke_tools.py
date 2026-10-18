"""冒烟：工具注册/查找/清单/执行（含异常不炸）。"""
import sys

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from hello_agents.tools.base import Tool
from hello_agents.tools.builtin.calculator import build_calculator_tool
from hello_agents.tools.registry import ToolRegistry


def broken_tool(text: str) -> str:
    raise RuntimeError("我故意炸的")


reg = ToolRegistry()
reg.register(build_calculator_tool())
reg.register(Tool(name="broken", description="故意报错的工具", func=broken_tool))
reg.register(Tool(name="echo", description="回显输入", func=lambda s: f"你说: {s}"))

print("=== 工具清单（给模型看）===")
print(reg.describe())
print("\n工具数:", len(reg.list_tools()))

print("\n=== 执行 ===")
for name, arg in [
    ("calculator", "(15*8+32)"),
    ("echo", "你好"),
    ("broken", "x"),
    ("no_such_tool", "?"),
]:
    found = reg.get(name)
    if found is None:
        print(f"{name}({arg!r}) -> 未找到")
    else:
        print(f"{name}({arg!r}) -> {found.run(arg)}")

print("\n✅ 第 4 步冒烟通过")
