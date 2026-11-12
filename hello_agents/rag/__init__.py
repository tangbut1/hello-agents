"""hello_agents.rag —— 从零实现的轻量 RAG：切块、检索、引用、回答。

不依赖向量数据库：用 BM25（中文按字符 bigram 切）做关键词检索，
把命中的原文按编号拼进上下文，要求模型只依据资料回答并标注引用。
"""
from .chunker import Chunk, chunk_text
from .retriever import BM25Retriever
from .agent import RAGAgent

__all__ = ["Chunk", "chunk_text", "BM25Retriever", "RAGAgent"]
