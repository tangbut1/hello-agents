"""rag/retriever.py —— 纯 Python BM25 检索器。

中文没有空格：把连续中文串切成字符 bigram（“向量检索” → 向量/量检/检索），
英文/数字按单词切。BM25 比“按关键词出现次数排序”更稳，因为它做了
词频饱和与文档长度归一化。
"""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import List, Tuple

from .chunker import Chunk

_WORD_RE = re.compile(r"[a-zA-Z0-9_]+")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]+")


def tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    tokens = _WORD_RE.findall(text)
    for run in _CJK_RE.findall(text):
        if len(run) == 1:
            tokens.append(run)
        else:
            tokens.extend(run[i : i + 2] for i in range(len(run) - 1))
    return tokens


class BM25Retriever:
    def __init__(self, chunks: List[Chunk], k1: float = 1.5, b: float = 0.75):
        if not chunks:
            raise ValueError("chunks 不能为空")
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self._docs = [tokenize(c.text) for c in chunks]
        self._tf = [Counter(d) for d in self._docs]
        self._dl = [len(d) for d in self._docs]
        self._avgdl = sum(self._dl) / len(self._dl)
        self._df: Counter = Counter()
        for d in self._docs:
            self._df.update(set(d))
        self._n = len(self._docs)

    def _idf(self, term: str) -> float:
        df = self._df.get(term, 0)
        return math.log(1 + (self._n - df + 0.5) / (df + 0.5))

    def search(self, query: str, top_k: int = 3) -> List[Tuple[Chunk, float]]:
        q_tokens = tokenize(query)
        if not q_tokens:
            return []
        scores: List[float] = []
        for i in range(self._n):
            score = 0.0
            dl = self._dl[i] or 1
            for term in q_tokens:
                tf = self._tf[i].get(term, 0)
                if not tf:
                    continue
                score += self._idf(term) * (
                    tf * (self.k1 + 1)
                    / (tf + self.k1 * (1 - self.b + self.b * dl / self._avgdl))
                )
            scores.append(score)
        ranked = sorted(range(self._n), key=lambda i: scores[i], reverse=True)
        out = []
        for i in ranked[:top_k]:
            if scores[i] > 0:
                out.append((self.chunks[i], round(scores[i], 4)))
        return out
