"""core/agent.py — 所有智能体的公共基类。

契约（每个智能体都必须遵守）：
1. 持有 llm（模型调用层）和 history（记忆）
2. 实现 run(user_input) -> str：怎么想、怎么行动，子类自己定
3. 记忆的增删查走基类方法（统一滑窗，防止上下文爆掉）
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .config import Config
from .llm import HelloAgentsLLM
from .message import Message, assistant, clip_history, system, to_openai, user


class Agent(ABC):
    """所有智能体的根。"""

    def __init__(
        self,
        llm: Optional[HelloAgentsLLM] = None,
        config: Optional[Config] = None,
        system_prompt: str = "",
        max_history: Optional[int] = None,
        name: str = "agent",
    ):
        self.config = config or Config.from_env()
        self.llm = llm or HelloAgentsLLM(**self.config.llm_kwargs())
        self.system_prompt = system_prompt
        self.max_history = max_history or self.config.max_history_messages
        self.name = name
        self.history: List[Message] = []
        if system_prompt:
            self.history.append(system(system_prompt))

    # ── 记忆管理（所有智能体共用一套规矩）──────────────────

    def add_message(self, message: Message) -> None:
        self.history.append(message)

    def add_user(self, content: str) -> None:
        self.add_message(user(content))

    def add_assistant(self, content: str) -> None:
        self.add_message(assistant(content))

    def clear_history(self, keep_system: bool = True) -> None:
        """清空记忆。默认保留系统人设。"""
        if keep_system and self.system_prompt:
            self.history = [system(self.system_prompt)]
        else:
            self.history = []

    def messages_for_llm(self) -> List[dict]:
        """给模型的对话快照：滑窗裁剪 + OpenAI 格式。"""
        return to_openai(clip_history(self.history, self.max_history))

    # ── 对外的对话入口 ────────────────────────────────────

    def chat(self, user_input: str) -> str:
        """一问一答：记用户 → 跑子类逻辑 → 记回答。"""
        self.add_user(user_input)
        reply = self.run(user_input)
        self.add_assistant(reply)
        return reply

    # ── 子类必须实现 ──────────────────────────────────────

    @abstractmethod
    def run(self, user_input: str) -> str:
        """处理一轮输入，返回回答文本。"""
        raise NotImplementedError
