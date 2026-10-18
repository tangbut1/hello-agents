"""冒烟测试：验证 message / config，并与 llm 串通（不真调模型）。"""
import sys

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from hello_agents import Config, Message, HelloAgentsLLM, system, user, assistant
from hello_agents.core.message import to_openai, clip_history

# 1) 配置：从环境变量读一次
cfg = Config.from_env()
print("配置:", cfg)

# 2) 消息：四种角色 + 预览
msgs = [
    system("你是购物参谋，回答必须带证据。"),
    user("降噪耳机怎么选？"),
    assistant("先看降噪深度和佩戴方式。"),
    user("预算一千，头戴式。"),
]
for m in msgs:
    print(m.preview)

# 3) 转换 + 滑窗
print("\nto_openai 前两条:", to_openai(msgs[:2]))
print("滑窗(保留3条):", [m.preview for m in clip_history(msgs, 3)])

# 4) 用配置构造 LLM 客户端（不真调用，只验证配置串通）
llm = HelloAgentsLLM(**cfg.llm_kwargs())
print(f"\nLLM 构造成功: {llm.provider} / {llm.model}")

# 5) 非法 role 必须被拦住
try:
    Message(role="robot", content="?")
    print("❌ 非法 role 没被拦住")
except ValueError as e:
    print(f"✅ 非法 role 被拦住: {e}")

print("\n✅ 第 2 步冒烟通过")
