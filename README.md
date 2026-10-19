# hello_agents —— 从零实现的智能体框架（学习项目）

跟随《Hello-Agents》第 7 章的学习实践：**不依赖 LangChain / LangGraph 等现成框架**，从零实现一个极简但完整的 Agent 框架，逐模块验证、逐步提交。

> 这是一个学习项目，代码以**可读性/教学性**为先（模块小、注释明确、每步配冒烟测试），不是生产级框架。

## 核心特性

- **多服务商 LLM 调用**：stepfun / deepseek 自动检测，OpenAI 兼容协议
- **💭💬 双路流式**：推理模型的「思考 / 回答」分两路实时输出
- **消息系统**：system / user / assistant / tool 统一封装，滑动窗口裁剪
- **记忆管理**：JSON 存档 / 恢复 / 中途注入（交互优先）
- **工具系统**：Tool + ToolRegistry，工具异常兜底（单个工具出错不中断 Agent）
- **ReAct 智能体**：思考 → 行动 → 观察循环，最大轮数限制、输出解析容错
- **真实工具接入**：多轨价格计算工具（封装自 AgentMart 项目的价格引擎）

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
