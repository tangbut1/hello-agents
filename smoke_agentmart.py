"""冒烟：框架 + AgentMart 价格引擎（第 7 步：汇合）。"""
import json
import sys

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from hello_agents import SimpleAgent
from hello_agents.tools.builtin.agentmart_price import agentmart_price, build_agentmart_price_tool
from hello_agents.tools.registry import ToolRegistry

# 0) 先直接验工具（不调模型）
raw = agentmart_price(
    json.dumps(
        {
            "list_price": "1000",
            "discounts": [
                {
                    "kind": "coupon",
                    "label": "店铺券",
                    "amount": "100",
                    "condition_kind": "unconditional",
                    "certainty": "page_public",
                    "layer": "shop",
                },
                {
                    "kind": "coupon",
                    "label": "平台券",
                    "amount": "50",
                    "condition_kind": "unconditional",
                    "certainty": "account_coupon",
                    "layer": "platform",
                },
            ],
        },
        ensure_ascii=False,
    )
)
print("工具直算:", raw)
res = json.loads(raw)
assert res["确定到手价"] == "850.00", res
assert res["公开轨"] == "900.00", res
assert res["账号权益差额"] == "50.00", res
print("✅ 工具直算正确（850 / 900 / 50）")

# 1) 挂进 SimpleAgent，真对话
reg = ToolRegistry()
reg.register(build_agentmart_price_tool())

calls = []
tool = reg.get("price_breakdown")
_orig = tool.func


def counting(expr: str) -> str:
    calls.append(expr)
    return _orig(expr)


tool.func = counting

agent = SimpleAgent(
    tools=reg,
    system_prompt="你是购物参谋。涉及算价时，必须调用 price_breakdown 工具，不要自己心算。",
    max_history=10,
    max_tool_iterations=5,
)

print("\n=== 对话 ===")
reply = agent.chat(
    "帮我算一下：耳机标价 1000 元，有店铺券 100 元（无条件、页面公开），"
    "平台券 50 元（只限我账号）。到手价多少？"
)
print("\n[最终回答]", reply)
assert calls, "模型没有调用 price_breakdown 工具"
assert "850" in reply, f"回答里没有确定到手价 850: {reply}"

print("\n✅ 第 7 步冒烟通过（框架 + AgentMart 价格工具）")
