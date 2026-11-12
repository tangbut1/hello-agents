"""rag/agent.py —— RAG 问答：检索 → 拼上下文 → 带引用回答。

设计取舍：
- 检索与生成分离：先 BM25 召回，再把命中的原文编号拼进 prompt；
- 引用可核对：返回结果里带 sources，答案里的 [1][2] 能对回原文；
- 没有模型也能用：缺 API Key 时退化为“返回检索到的原文”，不编答案。
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

from ..core.llm import HelloAgentsLLM
from .chunker import Chunk, chunk_text
from .retriever import BM25Retriever

RAG_SYSTEM_PROMPT = """你是一个只依据给定资料回答问题的助手。

规则：
1. 只使用资料中的信息；资料没有提到，就明确说“资料中没有提到”。
2. 每个结论后面用 [1]、[2] 标注依据的资料编号，不要编造编号。
3. 不要引入资料之外的知识，不要猜测。
"""


@dataclass
class RagAnswer:
    answer: str
    sources: List[Chunk]
    scores: List[float]


class RAGAgent:
    """最小 RAG：文档切块 → BM25 检索 → 带引用回答。"""

    def __init__(self, llm: Optional[HelloAgentsLLM] = None, top_k: int = 3):
        self.llm = llm
        self.top_k = top_k
        self._chunks: List[Chunk] = []
        self._retriever: Optional[BM25Retriever] = None

    # ── 入库 ────────────────────────────────────────────
    def add_text(self, text: str, source: str = "memory") -> int:
        chunks = chunk_text(text, source=source)
        self._chunks.extend(chunks)
        self._retriever = None
        return len(chunks)

    def add_file(self, path: Union[str, Path]) -> int:
        p = Path(path)
        return self.add_text(p.read_text(encoding="utf-8"), source=p.name)

    def add_directory(self, directory: Union[str, Path], pattern: str = "*.md") -> int:
        d = Path(directory)
        total = 0
        for p in sorted(d.glob(pattern)):
            total += self.add_file(p)
        return total

    @property
    def chunks(self) -> List[Chunk]:
        return list(self._chunks)

    def _ensure_retriever(self) -> BM25Retriever:
        if not self._chunks:
            raise ValueError("资料库为空：先 add_text / add_file / add_directory")
        if self._retriever is None:
            self._retriever = BM25Retriever(self._chunks)
        return self._retriever

    # ── 检索 ────────────────────────────────────────────
    def retrieve(self, question: str, top_k: Optional[int] = None) -> List[tuple]:
        return self._ensure_retriever().search(question, top_k or self.top_k)

    # ── 回答 ────────────────────────────────────────────
    def answer(self, question: str, use_llm: bool = True) -> RagAnswer:
        hits = self.retrieve(question)
        sources = [c for c, _ in hits]
        scores = [s for _, s in hits]

        if not hits:
            return RagAnswer("资料库中没有检索到相关内容。", [], [])

        context = "\n\n".join(
            f"[{i + 1}] 来源：{c.source}\n{c.text}" for i, c in enumerate(sources)
        )
        messages = [
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"资料：\n{context}\n\n问题：{question}\n\n请只依据资料回答，并用 [编号] 标注来源。",
            },
        ]

        fallback_reason = "（未启用模型）"
        if use_llm:
            fallback_reason = "（模型未返回有效回答）"
            try:
                llm = self.llm or HelloAgentsLLM()
                text = llm.think(messages, temperature=0.0)
                if text:
                    return RagAnswer(text.strip(), sources, scores)
                fallback_reason = "（模型返回为空）"
            except Exception as exc:  # 缺 Key / 网络失败都退化为原文
                fallback_reason = f"（模型不可用：{type(exc).__name__}）"

        extractive = "\n\n".join(
            f"[{i + 1}] {c.source}：{c.text}" for i, c in enumerate(sources)
        )
        return RagAnswer(
            f"{fallback_reason}返回检索到的原文：\n\n{extractive}",
            sources,
            scores,
        )
