"""冒烟：验证 Agent 基类（抽象/继承/记忆/滑窗）+ 一次真实 LLM 两轮对话。"""
import sys

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from hello_agents import Agent


class EchoAgent(Agent):
    """最小子类：不调模型，只回显，用来验证基类契约。"""

    def run(self, user_input: str) -> str:
        return f"echo: {user_input}"


class ChatAgent(Agent):
    """真实子类：把记忆喂给模型，回答。"""

    def run(self, user_input: str) -> str:
        reply = self.llm.think(self.messages_for_llm(), temperature=0.2)
        return reply or "(模型没有返回内容)"


# 1) 抽象基类不能被实例化
try:
    Agent()  # type: ignore
    print("❌ 抽象基类居然被实例化了")
except TypeError as e:
    print(f"✅ 抽象基类不能被实例化: {type(e).__name__}")

# 2) EchoAgent：记忆 + 滑窗 + chat()
a = EchoAgent(system_prompt="你是回显机器人", max_history=4)
print("chat1:", a.chat("你好"))
print("chat2:", a.chat("再说一次"))
print("历史条数（含 system）:", len(a.history))
print("滑窗后给模型的消息数:", len(a.messages_for_llm()))
a.clear_history()
print("清空后条数:", len(a.history))

# 3) ChatAgent：真实模型 + 记忆（第二轮验证它记不记得第一轮）
b = ChatAgent(system_prompt="你是简洁的助手，回答控制在一句话内。", max_history=10)
r1 = b.chat("我叫小明，请记住。")
print("\n[第1轮回答]", r1)
r2 = b.chat("我叫什么名字？")
print("\n[第2轮回答]", r2)
assert "小明" in r2, "记忆没生效：第二轮没记住名字"
print("\n✅ 第 3 步冒烟通过（记忆生效）")
