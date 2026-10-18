"""core/message.py — 框架的统一消息系统。

所有与模型的交互都走 Message：角色明确、可序列化、可追溯。
这是"消息记忆管理"的地基——以后 agent 的对话历史就是 Message 列表。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# 合法的消息角色（OpenAI 兼容接口认知的四种）
ROLES = ("system", "user", "assistant", "tool")


@dataclass
class Message:
    """一条消息。role 决定它是谁说的。

    system    = 系统指令（人设/规则）
    user      = 用户说的话
    assistant = 模型说的话
    tool      = 工具执行结果（需要 tool_call_id 对应是哪次调用）
    """

    role: str
    content: str = ""
    name: Optional[str] = None            # 工具消息/命名发言者
    tool_call_id: Optional[str] = None    # 工具消息对应的调用 id
    metadata: Dict[str, Any] = field(default_factory=dict)  # 扩展位（不喂给模型）
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self):
        if self.role not in ROLES:
            raise ValueError(f"非法 role: {self.role!r}，可选: {ROLES}")

    def to_dict(self) -> Dict[str, Any]:
        """转成 OpenAI 兼容的 dict。

        只带模型该看的字段（role/content/name/tool_call_id），
        框架自己的 metadata / created_at 不喂给模型。
        """
        d: Dict[str, Any] = {"role": self.role, "content": self.content}
        if self.name:
            d["name"] = self.name
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        return d

    @property
    def preview(self) -> str:
        """一行预览：调试/日志用，不污染控制台。"""
        text = self.content.replace("\n", " ")
        return f"[{self.role}] {text[:60]}{'…' if len(text) > 60 else ''}"


# ── 便捷构造（写起来短，读起来清楚）────────────────────────────

def system(content: str, **metadata: Any) -> Message:
    return Message(role="system", content=content, metadata=dict(metadata))


def user(content: str, **metadata: Any) -> Message:
    return Message(role="user", content=content, metadata=dict(metadata))


def assistant(content: str, **metadata: Any) -> Message:
    return Message(role="assistant", content=content, metadata=dict(metadata))


def tool(content: str, tool_call_id: str = "", **metadata: Any) -> Message:
    return Message(
        role="tool",
        content=content,
        tool_call_id=tool_call_id,
        metadata=dict(metadata),
    )


def to_openai(messages: List[Message]) -> List[Dict[str, Any]]:
    """批量转换：喂给 HelloAgentsLLM.think() 之前调用。"""
    return [m.to_dict() for m in messages]


def clip_history(messages: List[Message], max_messages: int) -> List[Message]:
    """历史滑窗：只保留最近 max_messages 条（系统消息永远保留）。

    这是"记忆管理"的第一道防线——防止对话无限膨胀吃爆上下文。
    """
    if max_messages <= 0:
        return messages
    system_msgs = [m for m in messages if m.role == "system"]
    others = [m for m in messages if m.role != "system"]
    keep = max(0, max_messages - len(system_msgs))
    return system_msgs + others[-keep:]
