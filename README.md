# hello_agents —— 从零实现的轻量 Agent 运行时

参考《Hello-Agents》第 7 章的路线，**不依赖 LangChain / LangGraph 等现成框架**，从零实现一个可读、可验证的 Agent 运行时：LLM 调用层、消息与滑窗、记忆存档、工具注册、ReAct 循环，逐模块验证、逐步提交。

> 定位：用来把“框架到底做了什么”拆开看清——模块小、注释明确、每步配冒烟测试；不是万能生产框架，适用边界见文末。

## 核心特性

- **多服务商 LLM 调用**：stepfun / deepseek 自动检测，OpenAI 兼容协议
- **💭💬 双路流式**：推理模型的「思考 / 回答」分两路实时输出
- **消息系统**：system / user / assistant / tool 统一封装，滑动窗口裁剪
- **记忆管理**：JSON 存档 / 恢复 / 中途注入（交互优先）
- **工具系统**：Tool + ToolRegistry，工具异常兜底（单个工具出错不中断 Agent）
- **ReAct 智能体**：思考 → 行动 → 观察循环，最大轮数限制、输出解析容错
- **真实工具接入**：多轨价格计算工具（封装自 AgentMart 项目的价格引擎）

## 本机运行验证（2026-11-12）

```text
$ python smoke_core.py
配置: Config(llm_provider='auto', model=None, ... max_history_messages=20)
[system] 你是购物参谋，回答必须带证据。
[user] 降噪耳机怎么选？
[assistant] 先看降噪深度和佩戴方式。
[user] 预算一千，头戴式。
滑窗(保留3条): ['[system] ...', '[assistant] ...', '[user] 预算一千，头戴式。']
LLM 构造成功: stepfun / step-3.7-flash
✅ 非法 role 被拦住: 非法 role: 'robot'
✅ 第 2 步冒烟通过

$ python smoke_tools.py
工具数: 3
calculator('(15*8+32)') -> (15*8+32) = 152
echo('你好') -> 你说: 你好
broken('x') -> 工具执行出错: 我故意炸的
no_such_tool('?') -> 未找到
✅ 第 4 步冒烟通过
```

## 目录结构

```
hello_agents/
├── core/
│   ├── llm.py        # 模型调用层（多服务商 + 双路流式）
│   ├── message.py    # 消息系统 + 历史滑窗
│   ├── config.py     # 集中配置（环境变量 → dataclass）
│   ├── memory.py     # 记忆：存档 / 恢复 / 注入
│   └── agent.py      # Agent 抽象基类（记忆 + run 契约）
├── tools/
│   ├── base.py       # Tool 基类
│   ├── registry.py   # 工具注册表
│   └── builtin/      # 内置工具（计算器、价格引擎桥接）
└── agents/
    └── simple_agent.py  # ReAct 工具调用循环
```

## 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 配置模型（复制模板后填入自己的 Key）
cp .env.example .env

# 3. 跑冒烟测试
uv run python smoke_llm.py        # 模型调用
uv run python smoke_core.py       # 消息 / 配置
uv run python smoke_agent.py      # Agent 基类 + 真实模型记忆
uv run python smoke_tools.py      # 工具系统
uv run python smoke_simple.py     # ReAct 工具调用循环
uv run python smoke_memory.py     # 记忆存档 / 恢复
uv run python smoke_agentmart.py  # 价格引擎工具接入（需 AgentMart 项目在相邻目录）
```

## 七步实现路线

| 步骤 | 模块 | 验证方式 |
|---|---|---|
| 1 | `core/llm.py` 模型调用层 | smoke_llm：真实调用 + 💭💬 流式 |
| 2 | `core/message.py` + `core/config.py` | smoke_core：消息构造、滑窗、配置 |
| 3 | `core/agent.py` 抽象基类 | smoke_agent：抽象不可实例化、跨轮记忆 |
| 4 | `tools/` 工具系统 | smoke_tools：注册 / 查找 / 异常不炸 |
| 5 | `agents/simple_agent.py` | smoke_simple：模型自主决定调工具（123×456=56088） |
| 6 | `core/memory.py` + 交互优先 | smoke_memory：存档 / 恢复 / 注入、跨实例记忆 |
| 7 | 与业务项目汇合 | smoke_agentmart：模型拼 JSON 调价格工具，算出 850 元到手价 |

## 设计原则

1. **极简依赖**：除 `openai` SDK 与 `python-dotenv` 外不引入任何框架
2. **渐进式**：每个模块可独立跑通，再拼装
3. **可测试**：每一步都有对应冒烟脚本
4. **交互优先**：记忆可随时存档、暂停、注入新约束

## 适用边界（当前版本）

- 只有**文本协议 ReAct**（`Action: 工具[参数]`），没有原生 `tool_calls` / 参数 schema 校验；
- 记忆是消息级 JSON 持久化，不支持执行中断 checkpoint 与“执行到哪一步”的状态恢复；
- 多服务商是**配置选择**，不是故障自动切换（failover）；
- 没有 MCP、多智能体协作、tracing/可观测、Agent 行为评测集——这些是下一步，不是已实现。

