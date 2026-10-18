"""core/config.py — 集中配置管理。

所有"可变的环境依赖"只在这里读一次，其他地方不再散落 os.getenv。
新增配置项 = 在这里加一个字段 + from_env 里加一行。
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """框架运行时配置。默认值就是"能跑"的那套。"""

    # ── 模型 ──
    llm_provider: str = "auto"          # auto / stepfun / deepseek
    model: Optional[str] = None         # 覆盖 provider 默认模型
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: float = 60.0
    temperature: float = 0.0

    # ── 框架行为 ──
    debug: bool = False
    max_history_messages: int = 20      # 记忆滑窗上限

    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量读取配置。没配的走默认值。"""
        return cls(
            llm_provider=os.getenv("LLM_PROVIDER", "auto"),
            model=os.getenv("LLM_MODEL") or None,
            api_key=os.getenv("LLM_API_KEY") or None,
            base_url=os.getenv("LLM_BASE_URL") or None,
            timeout=float(os.getenv("LLM_TIMEOUT", "60")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
            debug=os.getenv("LLM_DEBUG", "").lower() in ("1", "true", "yes"),
            max_history_messages=int(os.getenv("LLM_MAX_HISTORY", "20")),
        )

    def llm_kwargs(self) -> dict:
        """把配置打包成 HelloAgentsLLM 的构造参数。"""
        return dict(
            provider=self.llm_provider,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )
