# hello-agents 框架 · 建设计划（唯一总纲）

> 这是唯一的总纲文件。所有"接下来做什么"以本文件为准，不靠聊天记录。
> 修改本文件 = 修改计划。每完成一步，更新下面的进度表。

## 一、目标

造一个自己的智能体框架（第 7 章 HelloAgents 的致敬升级版），
最终服务于"交互式对比决策助手"产品（购物/旅游等场景的对比决策）。

框架的差异设计原则（来自产品魂）：
- **交互优先**：agent 每一步可存档、可暂停、可带着用户的修改继续
- **工具统一**：万事皆工具（检索、评估、浏览器、价格计算……）
- **证据优先**：输出必须能追溯

## 二、现状（截至 2026-10-17）

| 事项 | 状态 |
|---|---|
| 第 6 章（LangGraph）结业考试 | ✅ 通过 |
| AgentMart 项目跑通（browser 版，domain 层） | ✅ 115 个测试绿 |
| AgentMart domain 重构（P2） | ⏸ 暂缓（先建框架） |
| 产品定义（P0） | ⏸ 搁置（先建框架） |
| hello-agents 项目骨架 | ✅ 已建好（目录 + 依赖 + git） |

骨架现状：

```
D:\Study_ai\projects\hello-agents\
├── .env                    # 已从 ai-evidence-app 拷贝（含 MODEL_* 变量）
├── pyproject.toml          # openai + python-dotenv
├── hello_agents/
│   ├── __init__.py
│   └── core/
│       └── __init__.py
└── .git/                   # 已初始化并提交
```

## 三、总路线（7 步，顺序执行，不跳步）

| 步 | 内容 | 文件 | 验收标准 |
|---|---|---|---|
| 1 | HelloAgentsLLM：模型调用层（provider 自动检测 + 💭💬 流式） | `core/llm.py` | 真实调用一次，返回回答 |
| 2 | Message 类 + 配置管理 | `core/message.py`、`core/config.py` | 小测通过 |
| 3 | Agent 抽象基类 | `core/agent.py` | 子类可继承、run() 可覆写 |
| 4 | Tool + ToolRegistry（从第 8 站 ToolExecutor 升级） | `tools/` | 注册/查找/清单生成可用 |
| 5 | SimpleAgent：工具调用循环（Action→执行→Observation） | `agents/simple_agent.py` | 带一个计算器工具跑通 |
| 6 | Memory + 交互优先（可存档/可注入） | `core/memory.py` | 演示：跑一半存档，改状态继续 |
| 7 | 与 AgentMart 汇合：价格三件套做成工具挂载 | — | 对话式购物决策 MVP |

## 四、第 1 步（当前任务）：写 `core/llm.py`

**文件**：`D:\Study_ai\projects\hello-agents\hello_agents\core\llm.py`

**规格**（接口固定，实现自己写）：

```python
class HelloAgentsLLM:
    def __init__(self, provider="auto", model=None, api_key=None, base_url=None, timeout=None):
        ...

    def think(self, messages, temperature=0) -> str | None:
        ...
```

**五条要求**：

1. `provider="auto"` 按环境变量自动猜：有 `STEPFUN_API_KEY` 或 `MODEL_API_KEY` → stepfun；有 `OPENAI_API_KEY` → openai；都没有 → 报错说清楚缺什么
2. stepfun 兼容现有 `.env` 命名（`MODEL_API_KEY` / `MODEL_BASE_URL` / `MODEL_NAME`），不填新变量也能跑
3. 传的参数优先于环境变量（or 短路，沿用第 8 站风格）
4. 缺配置 fail-fast：`ValueError` 立刻炸
5. `think()` 原样保留第 8 站的💭💬双邮箱流式逻辑，一字不改

**参考**：`D:\Study_ai\projects\ai-evidence-app\ch4_react_agent.py` 第 14-64 行。

**验收**（我来跑）：

```python
llm = HelloAgentsLLM()          # auto 检测到 stepfun
r = llm.think([{"role": "user", "content": "用一句话解释什么是RAG"}])
assert r and len(r) > 10        # 真拿到了回答
```

**交付**（二选一）：
- A（推荐）：PyCharm 里自己写，写完说一声，我 review + 跑冒烟
- B：贴聊天里，我落盘 + review

## 五、工作纪律

1. **一次只写一个文件**。写完、跑绿、git commit，才进下一个。
2. **不跳步**。第 1 步没绿开第 2 步，就是给自己埋雷。
3. **卡住就贴报错**，我诊断。不硬猜。
4. **注释写人话**：每个函数头上写"它是干什么的"，不是"它怎么实现的"。

## 六、进度记录

| 日期 | 完成 | 备注 |
|---|---|---|
| 2026-10-16 | 骨架 + 本书计划 | — |
| 2026-10-17 | （第 1 步：llm.py —— 待完成） | — |
