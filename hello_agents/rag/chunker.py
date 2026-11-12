"""rag/chunker.py —— 把长文切成带来源的块。

切法：先按空行分段；段太长再按句子边界切，块之间保留少量重叠，
避免“答案刚好被切断”导致检索回来半句话。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Chunk:
    source: str          # 来源文件名 / 标题
    text: str            # 原文
    index: int           # 在该来源里的第几块


def _split_long(text: str, max_chars: int) -> List[str]:
    """按句号/问号/换行切，再把句子拼到不超过 max_chars。"""
    import re

    sentences = re.split(r"(?<=[。！？!?；;\n])", text)
    out, buf = [], ""
    for sent in sentences:
        if not sent.strip():
            continue
        if len(buf) + len(sent) <= max_chars:
            buf += sent
        else:
            if buf:
                out.append(buf)
            buf = sent
    if buf:
        out.append(buf)
    return out


def chunk_text(
    text: str,
    source: str = "unknown",
    max_chars: int = 500,
    overlap: int = 80,
) -> List[Chunk]:
    """把一段文本切成 Chunk 列表。"""
    text = (text or "").strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    pieces: List[str] = []
    for para in paragraphs:
        if len(para) <= max_chars:
            pieces.append(para)
        else:
            pieces.extend(_split_long(para, max_chars))

    chunks: List[Chunk] = []
    for i, piece in enumerate(pieces):
        if i > 0 and overlap > 0:
            # 从上一块尾部取一点重叠，帮助跨块问题检索
            prev_tail = pieces[i - 1][-overlap:]
            piece = prev_tail + "\n" + piece
        chunks.append(Chunk(source=source, text=piece.strip(), index=i))
    return chunks
