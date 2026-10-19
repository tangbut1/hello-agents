"""core/memory.py — 记忆：对话历史的容器 + 存档/恢复。

交互优先（产品魂）的地基：
- 快照 snapshot()：把当前记忆存成可序列化的 dict
- 存档 save() / 恢复 load()：记忆跨进程、跨实例存活
- 注入 inject()（在 Agent 上）：用户中途插话，带着新要求继续
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Union

from .message import Message, clip_history, to_openai

SCHEMA_VERSION = 1


class Memory:
    """对话记忆：按时间顺序追加 Message，支持滑窗、存档、恢复。"""

    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self._messages: List[Message] = []

    # ── 基本操作 ──────────────────────────────────────────

    def add(self, message: Message) -> None:
        self._messages.append(message)

    def messages(self) -> List[Message]:
        return list(self._messages)

    def for_llm(self) -> List[dict]:
        """给模型的快照：滑窗裁剪 + OpenAI 格式。"""
        return to_openai(clip_history(self._messages, self.max_messages))

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)

    # ── 存档 / 恢复（交互优先）────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        """当前记忆的可序列化快照。"""
        return {
            "version": SCHEMA_VERSION,
            "max_messages": self.max_messages,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "name": m.name,
                    "tool_call_id": m.tool_call_id,
                    "metadata": m.metadata,
                    "created_at": m.created_at,
                }
                for m in self._messages
            ],
        }

    def restore(self, data: Dict[str, Any]) -> int:
        """从快照恢复记忆。返回恢复的消息条数。"""
        if not isinstance(data, dict) or "messages" not in data:
            raise ValueError("快照格式不对：需要一个带 messages 字段的 dict")
        self.max_messages = int(data.get("max_messages", self.max_messages))
        restored: List[Message] = []
        for item in data["messages"]:
            kwargs = dict(
                role=item["role"],
                content=item.get("content", ""),
                name=item.get("name"),
                tool_call_id=item.get("tool_call_id"),
                metadata=item.get("metadata") or {},
            )
            if item.get("created_at"):
                kwargs["created_at"] = item["created_at"]
            restored.append(Message(**kwargs))
        self._messages = restored
        return len(restored)

    def save(self, path: Union[str, Path]) -> Path:
        """存档到 JSON 文件。"""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(self.snapshot(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return p

    def load(self, path: Union[str, Path]) -> int:
        """从 JSON 文件恢复记忆。"""
        p = Path(path)
        return self.restore(json.loads(p.read_text(encoding="utf-8")))
