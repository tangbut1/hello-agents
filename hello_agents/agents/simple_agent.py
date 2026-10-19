"""agents/simple_agent.py — 最简单但完整的智能体：会调工具的思考-行动循环。

流程（ReAct 范式）：
    思考 Thought → 行动 Action（调工具/Finish）→ 观察 Observation → 再思考……
直到模型输出 Finish[最终答案] 或达到最大工具调用次数。

它和基类 Agent 的关系：
- 基类管记忆（history/滑窗/chat 一问一答）
- 子类管"这一轮怎么想、怎么行动"（run 的实现）
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from ..core.agent import Agent
from ..core.message import clip_history, to_openai
from ..tools.registry import ToolRegistry

TOOLS_SYSTEM_TEMPLATE = """你是一个会使用工具的智能体。
可用工具如下：
{tools}

请严格按照以下格式回应（只输出这两行，不要输出其他内容）：
Thought: 你的思考过程
Action: 需要调用工具时写 tool_name[参数]；可以直接回答时写 Finish[最终答案]
"""


class SimpleAgent(Agent):
    """会调工具的智能体：思考 → 行动 → 观察，循环到出答案。"""

    def __init__(
        self,
        tools: Optional[ToolRegistry] = None,
        max_tool_iterations: int = 5,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.tools = tools or ToolRegistry()
        self.max_tool_iterations = max_tool_iterations

    def has_tools(self) -> bool:
        return len(self.tools.list_tools()) > 0

    # ── 提示词构造 ────────────────────────────────────────

    def _build_messages(self, question: str, observations: str) -> List[dict]:
        system_text = TOOLS_SYSTEM_TEMPLATE.format(
            tools=self.tools.describe() or "（无可用工具）"
        )
        if self.system_prompt:
            system_text = self.system_prompt + "\n\n" + system_text

        msgs: List[dict] = [{"role": "system", "content": system_text}]

        # 之前的对话（不含系统消息与本轮问题）——多轮记忆在这里生效
        past = [m for m in self.history if m.role != "system"]
        if past:
            msgs.extend(to_openai(clip_history(past[:-1], self.max_history)))

        user_text = f"Question: {question}"
        if observations:
            user_text += f"\n\n已完成的过程:\n{observations}"
        msgs.append({"role": "user", "content": user_text})
        return msgs

    # ── 主循环 ────────────────────────────────────────────

    def run(self, user_input: str) -> str:
        observations = ""

        for _ in range(self.max_tool_iterations):
            response = self.llm.think(
                self._build_messages(user_input, observations), temperature=0.2
            )
            if not response:
                return "（模型没有返回有效响应）"

            action = self._parse_action(response)
            if action is None:
                # 模型没按格式来：把整段当回答（宽容处理，不硬报错）
                return response.strip()

            action_name, action_arg = action
            if action_name == "Finish":
                return action_arg

            tool = self.tools.get(action_name)
            if tool is None:
                observation = (
                    f"错误：没有名为 '{action_name}' 的工具。"
                    f"可用工具：{self.tools.describe()}"
                )
            else:
                observation = tool.run(action_arg)

            print(f"  [工具] {action_name}({action_arg}) -> {observation}")
            observations += f"\nAction: {action_name}[{action_arg}]\nObservation: {observation}"

        return (
            f"超过最大工具调用次数（{self.max_tool_iterations}），"
            f"最后观察：{observations.strip()}"
        )

    # ── 输出解析 ──────────────────────────────────────────

    @staticmethod
    def _parse_action(text: str) -> Optional[Tuple[str, str]]:
        """从模型输出解析 Action。

        返回：
            ("Finish", 最终答案)  —— 模型认为可以直接回答
            (工具名, 参数)        —— 模型要调工具
            None                  —— 没按格式来
        """
        match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        if not match:
            return None
        action = match.group(1).strip()

        if action.startswith("Finish"):
            finish = re.match(r"Finish\[(.*)\]", action, re.DOTALL)
            return ("Finish", finish.group(1).strip()) if finish else ("Finish", action)

        call = re.match(r"(\w+)\[(.*)\]", action, re.DOTALL)
        if call:
            return (call.group(1), call.group(2))
        return None
