"""core/llm.py — 框架的模型调用层（HelloAgentsLLM 升级版）。

把"连哪个模型服务"从写死变成可配置。
- provider="auto"：按环境变量自动检测
- 支持：stepfun / openai
- 保留第 8 站 think() 的 💭💬 双邮箱流式直播
"""
from __future__ import annotations

import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# provider 注册表：名字 -> 配置来源
# 约定：传参优先 > 本 provider 专属环境变量 > 兼容的旧变量(MODEL_*)
PROVIDERS: Dict[str, Dict] = {
    "stepfun": {
        "env_key": "STEPFUN_API_KEY",
        "fallback_key": "MODEL_API_KEY",      # 兼容现有 .env
        "default_base_url": "https://api.stepfun.com/v1",
        "fallback_base_url": "MODEL_BASE_URL",
        "default_model": "step-3.7-flash",
        "fallback_model": "MODEL_NAME",
    },
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "fallback_key": None,
        "default_base_url": "https://api.openai.com/v1",
        "fallback_base_url": None,
        "default_model": "gpt-4o-mini",
        "fallback_model": None,
    },
}


class HelloAgentsLLM:
    """LLM 客户端：根据 provider 连接对应的 OpenAI 兼容服务。"""

    def __init__(
        self,
        provider: str = "auto",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        # TODO 1: provider == "auto" 时调用 self._auto_detect_provider()
        # TODO 2: 按 provider 从 PROVIDERS 表解析 model / api_key / base_url
        #         （参数 > 专属环境变量 > fallback 环境变量 > 默认值）
        # TODO 3: 缺配置 raise ValueError，说清楚缺哪个
        # TODO 4: self.client = OpenAI(api_key=..., base_url=..., timeout=...)
        raise NotImplementedError("第 1 步：填写 __init__")

    def _auto_detect_provider(self) -> str:
        """按环境变量猜 provider。猜不出就报错说明缺什么。"""
        # TODO: STEPFUN_API_KEY 或 MODEL_API_KEY -> "stepfun"
        #       OPENAI_API_KEY -> "openai"
        #       都没有 -> raise ValueError
        raise NotImplementedError("第 1 步：填写自动检测")

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> Optional[str]:
        """调模型思考：流式，💭 reasoning_content 与 💬 content 分开直播。

        TODO: 把 ch4_react_agent.py 第 27-64 行搬过来，逻辑不改：
              流式接收 -> reasoning 打💭 -> content 打💬并收集 -> 返回 content 全文
        """
        raise NotImplementedError("第 1 步：填写 think()")
