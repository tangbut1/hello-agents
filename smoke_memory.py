"""冒烟：记忆存档/恢复/注入（交互优先地基）+ 跨实例真实记忆。"""
import sys
import tempfile
from pathlib import Path

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from hello_agents import Agent, Memory
from hello_agents.core.message import system, user


class EchoAgent(Agent):
    def run(self, user_input: str) -> str:
        return f"echo: {user_input}"


class ChatAgent(Agent):
    def run(self, user_input: str) -> str:
        return self.llm.think(self.messages_for_llm(), temperature=0.2) or "(空)"


# 1) Memory 单元：加消息 + 快照
m = Memory(max_messages=5)
m.add(system("你是助手"))
m.add(user("第一条"))
print("Memory 单元：", len(m.messages()), "条；快照消息数：", len(m.snapshot()["messages"]))

# 2) EchoAgent：chat → 存档 → 新实例恢复
a = EchoAgent(system_prompt="你是回显机器人", max_history=10)
a.chat("你好")
path = Path(tempfile.gettempdir()) / "hello_agents_memory_test.json"
a.save_state(path)
print("存档文件：", path, "大小：", path.stat().st_size, "字节")

b = EchoAgent(max_history=10)  # 不传 system_prompt——从存档里读回
b.load_state(path)
print("恢复后历史：", [msg.preview for msg in b.history])
assert len(b.history) == len(a.history), "恢复的历史条数不一致"

# 3) 交互优先：中途注入新要求
b.inject("额外要求：以后回答都用繁体中文")
print("注入后最后一条：", b.history[-1].preview)

# 4) 真实模型：记忆跨实例存活
c = ChatAgent(system_prompt="你是简洁的助手", max_history=10)
c.chat("我叫小明，记住我的名字。")
c.save_state(path)

d = ChatAgent(system_prompt="你是简洁的助手", max_history=10)
d.load_state(path)
r = d.chat("我叫什么名字？")
print("\n[新实例回答]", r)
assert "小明" in r, "记忆恢复失败：新实例没记住名字"

print("\n✅ 第 6 步冒烟通过（存档 / 恢复 / 注入）")
