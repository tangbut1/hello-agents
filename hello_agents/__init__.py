"""hello_agents — 自己的智能体框架（HelloAgents 致敬版）。

公共 API:
    HelloAgentsLLM  — 模型调用层（provider 自动检测）
    Config          — 集中配置（环境变量 → dataclass）
    Message         — 统一消息（+ system/user/assistant/tool 便捷构造）
"""
from .core.llm import HelloAgentsLLM
from .core.config import Config
from .core.message import Message, system, user, assistant, tool

__all__ = [
    "HelloAgentsLLM",
    "Config",
    "Message",
    "system",
    "user",
    "assistant",
    "tool",
]
