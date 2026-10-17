"""core/llm.py — 框架的模型调用层（HelloAgentsLLM 升级版）。

把"连哪个模型服务"从写死变成可配置。
- provider="auto"：按环境变量自动检测
- 支持：stepfun / deepseek
- 保留第 8 站 think() 的 💭💬 双邮箱流式直播
"""
from __future__ import annotations

import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# provider 注册表：名字 -> 配置来源
# 约定：传参优先 > 本 provider 专属环境变量 > 兼容的旧变量(MODEL_*) > 默认值
PROVIDERS: Dict[str, Dict] = {
    "stepfun": {
        "env_key": "STEPFUN_API_KEY",
        "fallback_key": "MODEL_API_KEY",      # 兼容现有 .env
        "base_url": "https://api.stepfun.com/v1",
        "fallback_base_url": "MODEL_BASE_URL",
        "model": "step-3.7-flash",
        "fallback_model": "MODEL_NAME",
    },
    "deepseek": {
        "env_key": "DEEPSEEK_API_KEY",
        "fallback_key": None,
        "base_url": "https://api.deepseek.com/v1",
        "fallback_base_url": None,
        "model": "deepseek-chat",
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
        # 1) 自动检测服务商
        if provider == "auto":
            provider = self._auto_detect_provider()
        if provider not in PROVIDERS:
            raise ValueError(f"未知 provider: {provider!r}，可选: {list(PROVIDERS)}")

        conf = PROVIDERS[provider]

        # 2) 解析配置：传参 > 专属环境变量 > 兼容环境变量 > 默认值
        api_key = api_key or os.getenv(conf["env_key"])
        if not api_key and conf.get("fallback_key"):
            api_key = os.getenv(conf["fallback_key"])

        fallback_base_url = (
            os.getenv(conf["fallback_base_url"]) if conf.get("fallback_base_url") else None
        )
        base_url = base_url or fallback_base_url or conf["base_url"]

        fallback_model = (
            os.getenv(conf["fallback_model"]) if conf.get("fallback_model") else None
        )
        model = model or fallback_model or conf["model"]

        timeout = timeout or float(os.getenv("LLM_TIMEOUT", "60"))

        # 3) 缺配置 fail-fast
        if not all([model, api_key, base_url]):
            raise ValueError(
                f"provider={provider} 缺少配置："
                f"model={model!r}, api_key={'已配置' if api_key else '缺失'}, base_url={base_url!r}"
            )

        # 4) 创建客户端
        self.provider = provider
        self.model = model
        self.base_url = base_url
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def _auto_detect_provider(self) -> str:
        """按环境变量猜 provider。猜不出就报错说明缺什么。"""
        if os.getenv("STEPFUN_API_KEY") or os.getenv("MODEL_API_KEY"):
            return "stepfun"
        if os.getenv("DEEPSEEK_API_KEY"):
            return "deepseek"
        raise ValueError(
            "无法自动检测 provider：请设置 STEPFUN_API_KEY、MODEL_API_KEY 或 DEEPSEEK_API_KEY"
        )

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> Optional[str]:
        """调模型思考：流式，💭 reasoning_content 与 💬 content 分开直播。

        返回 content 拼成的全文；出错返回 None（不炸整个流程）。
        """
        print(f"正在调用 {self.model} 模型 ...")
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            collected_content: List[str] = []
            in_thinking = False
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                # 老版本 SDK 的 delta 可能没有 reasoning_content，getattr 兜底
                thought = getattr(delta, "reasoning_content", None) or ""
                answer = delta.content or ""
                if thought:
                    if not in_thinking:  # 独白开始，打一次标记
                        print("\n💭 [思考中] ", end="", flush=True)
                        in_thinking = True
                    print(thought, end="", flush=True)
                if answer:
                    if in_thinking:  # 答案开始，切换标记
                        print("\n\n💬 [作答] ", end="", flush=True)
                        in_thinking = False
                    print(answer, end="", flush=True)
                    collected_content.append(answer)
            print()
            return "".join(collected_content)
        except Exception as e:
            print(f"❌ 调用 LLM API 时发生错误: {e}")
            return None
