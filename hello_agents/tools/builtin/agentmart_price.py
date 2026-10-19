"""tools/builtin/agentmart_price.py — 把 AgentMart 的价格引擎挂成框架工具。

输入：JSON 字符串（商品 + 优惠清单）
输出：多轨到手价（确定性代码计算，不做心算）

JSON 示例：
{
  "list_price": "1000",
  "shipping_fee": "0",
  "discounts": [
    {"kind": "coupon", "label": "店铺券", "amount": "100",
     "condition_kind": "unconditional", "certainty": "page_public", "layer": "shop"},
    {"kind": "coupon", "label": "平台券", "amount": "50",
     "condition_kind": "unconditional", "certainty": "account_coupon", "layer": "platform"}
  ]
}
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from ..base import Tool

# 默认位置：projects/AgentMart/AgentMart-main/agentmart-browser（与本项目同级）
_DEFAULT_ROOT = (
    Path(__file__).resolve().parents[4]
    / "AgentMart"
    / "AgentMart-main"
    / "agentmart-browser"
)


def _agentmart_root() -> Path:
    return Path(os.getenv("AGENTMART_ROOT", str(_DEFAULT_ROOT)))


def _load_domain():
    """延迟导入 AgentMart 的 domain 层（不依赖它被 pip 安装）。"""
    root = _agentmart_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from app.domain.enums import (  # type: ignore
        ConditionKind,
        DataStatus,
        DiscountKind,
        DiscountLayer,
        Platform,
        PriceCertainty,
    )
    from app.domain.models import Discount, Offer  # type: ignore
    from app.domain.pricing import compute_price_breakdown  # type: ignore

    return {
        "ConditionKind": ConditionKind,
        "DataStatus": DataStatus,
        "DiscountKind": DiscountKind,
        "DiscountLayer": DiscountLayer,
        "Platform": Platform,
        "PriceCertainty": PriceCertainty,
        "Discount": Discount,
        "Offer": Offer,
        "compute_price_breakdown": compute_price_breakdown,
    }


def _build_offer(data: Dict[str, Any]):
    dom = _load_domain()
    offer = dom["Offer"](
        platform=dom["Platform"](data.get("platform", "jd")),
        platform_product_id=str(data.get("id", "demo")),
        title=str(data.get("title", "演示商品")),
        url=str(data.get("url", "https://example.com/demo")),
        list_price=str(data["list_price"]),
        shipping_fee=str(data.get("shipping_fee", "0")),
        data_status=dom["DataStatus"].REAL,
    )
    discounts = []
    for item in data.get("discounts", []):
        kwargs = dict(
            kind=dom["DiscountKind"](item.get("kind", "coupon")),
            label=str(item.get("label", "优惠")),
            amount=str(item.get("amount", "0")),
            condition_kind=dom["ConditionKind"](
                item.get("condition_kind", "unconditional")
            ),
        )
        if item.get("certainty"):
            kwargs["certainty"] = dom["PriceCertainty"](item["certainty"])
        if item.get("layer"):
            kwargs["layer"] = dom["DiscountLayer"](item["layer"])
        discounts.append(dom["Discount"](**kwargs))
    offer.discounts = discounts
    return offer


def agentmart_price(expr: str) -> str:
    """工具执行函数：JSON 输入 -> 多轨价格 JSON 输出。"""
    try:
        data = json.loads(expr)
    except json.JSONDecodeError as e:
        return (
            f"错误：输入不是合法 JSON（{e}）。"
            '示例：{"list_price":"1000","discounts":[{"kind":"coupon","label":"店铺券",'
            '"amount":"100","condition_kind":"unconditional","certainty":"page_public","layer":"shop"}]}'
        )

    try:
        dom = _load_domain()
        offer = _build_offer(data)
        breakdown = dom["compute_price_breakdown"](offer)
        return json.dumps(
            {
                "确定到手价": str(breakdown.definite_total),
                "公开轨": str(breakdown.public_total),
                "潜在价": str(breakdown.potential_total),
                "无法核实": str(breakdown.unverifiable_total),
                "账号权益差额": str(breakdown.account_gap),
                "notes": breakdown.notes,
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return f"错误：价格计算失败（{type(e).__name__}: {e}）"


def build_agentmart_price_tool() -> Tool:
    """构造购物价格工具。"""
    return Tool(
        name="price_breakdown",
        description=(
            "计算一个商品的多轨到手价（确定性代码，不做心算）。输入 JSON 字符串："
            '{"list_price":"1000","shipping_fee":"0","discounts":['
            '{"kind":"coupon","label":"店铺券","amount":"100",'
            '"condition_kind":"unconditional","certainty":"page_public","layer":"shop"}]}。'
            "kind 可选 coupon/activity/payment/trade_in/free_shipping/subsidy；"
            "condition_kind 可选 unconditional/conditional/unverifiable；"
            "certainty 可选 page_public/account_coupon/conditional/prepayment/unverifiable；"
            "layer 可选 product/shop/platform/payment/subsidy/shipping。"
        ),
        func=agentmart_price,
    )
