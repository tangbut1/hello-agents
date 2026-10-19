"""冒烟：SimpleAgent 工具调用循环（该调工具的 + 不该调工具的）。"""
import sys

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from hello_agents import SimpleAgent
from hello_agents.tools.builtin.calculator import build_calculator_tool
from hello_agents.tools.registry import ToolRegistry

reg = ToolRegistry()
reg.register(build_calculator_tool())

agent = SimpleAgent(
    tools=reg,
    system_prompt="你是一个简洁的助手。",
    max_history=10,
    max_tool_iterations=5,
)

print("=== 测试 1：需要工具的问题 ===")
r1 = agent.chat("请用计算器算一下 123 乘以 456 等于多少？只给最终数字答案。")
print("\n[最终回答]", r1)
assert "56088" in r1.replace(",", ""), f"预期 56088，实际: {r1}"

print("\n=== 测试 2：不需要工具的问题 ===")
r2 = agent.chat("用一句话解释什么是RAG。")
print("\n[最终回答]", r2)
assert len(r2) > 5, f"回答太短: {r2}"

print("\n✅ 第 5 步冒烟通过（工具调用 + 直接回答）")
