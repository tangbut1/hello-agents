"""core/agent.py — 所有智能体的公共基类。

契约（每个智能体都必须遵守）：
1. 持有 llm（模型调用层）和 memory（记忆）
2. 实现 run(user_input) -> str：怎么想、怎么行动，子类自己定
3. 记忆的增删查走基类方法（统一滑窗，防止上下文爆掉）

交互优先（产品魂）：
- save_state() / load_state()：记忆存档，跨实例继续对话
- inject()：用户中途插入要求，带着新约束继续
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Union
from pathlib import Path

from .config import Config
from .llm import HelloAgentsLLM
from .memory import Memory
from .message import Message, assistant, system, user


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
        self.memory = Memory(max_messages=self.max_history)
        if system_prompt:
            self.memory.add(system(system_prompt))

    # ── 记忆管理（所有智能体共用一套规矩）──────────────────

    @property
    def history(self) -> List[Message]:
        return self.memory.messages()

    def add_message(self, message: Message) -> None:
        self.memory.add(message)

    def add_user(self, content: str) -> None:
        self.add_message(user(content))

    def add_assistant(self, content: str) -> None:
        self.add_message(assistant(content))

    def clear_history(self, keep_system: bool = True) -> None:
        """清空记忆。默认保留系统人设。"""
        self.memory.clear()
        if keep_system and self.system_prompt:
            self.memory.add(system(self.system_prompt))

    def messages_for_llm(self) -> List[dict]:
        """给模型的对话快照：滑窗裁剪 + OpenAI 格式。"""
        return self.memory.for_llm()

    # ── 交互优先：存档 / 恢复 / 注入 ──────────────────────

    def save_state(self, path: Union[str, Path]) -> Path:
        """把当前记忆存档到文件。"""
        return self.memory.save(path)

    def load_state(self, path: Union[str, Path]) -> int:
        """从文件恢复记忆。返回恢复的消息条数。"""
        return self.memory.load(path)

    def inject(self, content: str, role: str = "user") -> None:
        """中途注入一条消息（用户的临时新要求、纠正、补充条件）。"""
        self.memory.add(Message(role=role, content=content))

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
