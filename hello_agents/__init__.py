"""hello_agents — 自己的智能体框架（HelloAgents 致敬版）。

公共 API:
    HelloAgentsLLM  — 模型调用层（provider 自动检测）
    Config          — 集中配置（环境变量 → dataclass）
    Message         — 统一消息（+ system/user/assistant/tool 便捷构造）
    Agent           — 所有智能体的抽象基类
    SimpleAgent     — 会调工具的智能体
"""
from .agents import SimpleAgent
from .core.agent import Agent
from .core.config import Config
from .core.llm import HelloAgentsLLM
from .core.message import Message, assistant, system, tool, user

__all__ = [
    "HelloAgentsLLM",
    "Config",
    "Message",
    "Agent",
    "SimpleAgent",
    "system",
    "user",
    "assistant",
    "tool",
]
