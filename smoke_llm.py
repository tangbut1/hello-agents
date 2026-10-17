"""冒烟测试：验证 HelloAgentsLLM 能真实连上并拿到回答。"""
import sys

# Windows 控制台默认 GBK，💭💬 会崩；强制 UTF-8 输出
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from hello_agents.core.llm import HelloAgentsLLM

llm = HelloAgentsLLM()  # provider="auto"
print(f"provider={llm.provider}, model={llm.model}, base_url={llm.base_url}\n")

r = llm.think([{"role": "user", "content": "用一句话解释什么是RAG（检索增强生成）"}])
print("\n=== 返回内容 ===")
print(r)
assert r and len(r) > 10, "冒烟失败：没有拿到有效回答"
print("\n✅ 冒烟通过")
