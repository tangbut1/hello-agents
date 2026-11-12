"""smoke_rag.py —— 第 8 步：RAG 冒烟（切块 → BM25 检索 → 带引用回答）。

默认离线：不调用模型，只验证检索与引用；
加 --llm 才真实调用模型生成答案（会消耗 token）。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from hello_agents.rag import RAGAgent  # noqa: E402

CORPUS = ROOT / "examples" / "rag" / "corpus"


def main() -> int:
    use_llm = "--llm" in sys.argv
    agent = RAGAgent(top_k=3)
    n = agent.add_directory(CORPUS)
    print(f"资料入库：{n} 个块，来自 {len(list(CORPUS.glob('*.md')))} 个文件")

    cases = [
        ("AgentMart 为什么把金额交给确定性代码？", "agentmart-price.md"),
        ("MarketPulse 的 Wilson 置信区间解决什么问题？", "marketpulse.md"),
        ("hello_agents 的 ReAct 最大轮数是多少？", "agent-runtime.md"),
        ("RAG 为什么要保留引用？", "rag-basics.md"),
    ]

    ok = True
    for question, expected in cases:
        hits = agent.retrieve(question)
        sources = [c.source for c, _ in hits]
        hit = expected in sources
        ok = ok and hit
        print(f"\nQ: {question}")
        print("  命中:", [(c.source, s) for c, s in hits])
        print("  期望来源:", expected, "→", "✅" if hit else "❌")

    result = agent.answer(cases[0][0], use_llm=use_llm)
    print("\n=== 回答（use_llm=%s）===" % use_llm)
    print(result.answer[:800])
    print("来源:", [c.source for c in result.sources])

    print("\n" + ("✅ 第 8 步 RAG 冒烟通过" if ok else "❌ RAG 冒烟失败"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
