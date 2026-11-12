# hello_agents 运行时

hello_agents 是一个从零实现的轻量 Agent 运行时，不依赖 LangChain / LangGraph。

## 核心模块

- `core/llm.py`：多服务商 LLM 调用层，支持 stepfun / deepseek，OpenAI 兼容协议；推理模型把「思考」与「回答」做双路流式输出。
- `core/message.py`：system / user / assistant / tool 统一封装；按条数做滑动窗口裁剪，保留 system 消息。
- `core/memory.py`：记忆的 JSON 存档、恢复与中途注入；交互优先，可随时暂停并注入新约束。
- `tools/base.py` 与 `tools/registry.py`：Tool 基类与工具注册表；单个工具抛异常不会中断 Agent，异常会作为 Observation 回填。
- `agents/simple_agent.py`：文本协议 ReAct 循环，模型输出 `Action: 工具[参数]` 或 `Finish[答案]`；最大工具调用轮数默认 5。

## 边界

当前版本只有文本协议 ReAct，没有原生 tool_calls 与参数 schema 校验；多服务商是配置选择，不是故障自动切换；没有 MCP、多智能体、tracing 与 Agent 行为评测。
