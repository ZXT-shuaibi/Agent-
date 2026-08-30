---
name: agent-chain-scan
description: Use when a Python/LLM/Agent repository needs static discovery of orchestration, tools, long-running state, memory, evaluation, observability, or security chains.
---

# Agent 源码链路扫描

> 内部 ID：`agent-chain-scan`

## 作用

从 Python/LLM/Agent 项目的本地源码中，定位“入口 → 编排/状态 → 模型决策 → Tool/RAG → 持久化副作用 → 评测/观测 → 用户交付”的可验证链路。它是静态证据扫描器，不是代码运行器。

## 输入

- 本地项目目录或已解压的源码；
- 可选的目标业务方向，例如客服、企业知识或 DevOps；
- 不需要先告诉我框架，扫描器会识别常见模式。

## 输出

- `frameworks`、`entrypoints`、`evidence`、`chains`；
- 每个证据点的文件路径、行号、符号和摘录；
- 未知框架的 `candidate_patterns` 和 `rule_update_proposal`；
- 每条候选链路的“为什么是亮点”、业务后果、适合承载背景、源码嵌入点和最小重实现；
- 无法由源码确认的部分标为 `[待确认]`。

## 何时使用

你能提供源码，并且希望知道“真正能写进项目经历的工程链路”时使用。没有源码时改用 Agent 口述链路提取。

## 怎么用

说：“使用 `agent-chain-scan` 扫描 `C:\\work\\my-agent`，重点看长程任务、Tool 可靠性和评测。”插件会先运行 [源码扫描器](../../scripts/scan_agent_repo.py)，再基于本地证据解释业务价值。

从 Agent 能力入口切入，不寻找 Java Controller。先运行源码扫描器，再只对本地证据做业务解释。

## 四阶段扫描法

### 1. 找入口和业务对象

先定位 FastAPI/Flask/Django route、CLI、worker、webhook、WebSocket 和消息消费者，再确认它接收的是任务、案件、文档、指标、事件还是其他对象。只找到 `main()` 或 `app = FastAPI()` 不能证明业务入口成立。

### 2. 追执行图和状态

沿入口最多追 4 层调用，记录任务分解、graph/node、状态 schema、队列、checkpoint/store、恢复/取消和终态。对每个状态回答“谁写入、谁读取、进程重启后是否还存在”。只有 `StateGraph` 或 `asyncio.create_task`，没有持久化和终态时，不能写成长程任务亮点。

### 3. 追 Tool/RAG 和副作用

区分只读与写入 Tool，记录 schema、参数校验、权限、租户、超时、重试、幂等、补偿、审计和人工确认。RAG 要追 ingestion、版本、ACL、召回/重排、引用和回滚。装饰器、注册表或 README 只证明候选存在，必须回读函数正文确认调用关系和副作用。

### 4. 追评测、观测和证据闭环

查找 eval dataset、trajectory、grader、阈值、CI、trace、token/cost、延迟、告警和失败样本回流。把证据按“入口 → 编排/状态 → Tool/RAG/副作用 → 评测/观测”分段；至少 5 个证据点覆盖 3 段后，才能给出高含金量结论。

每条候选最终都输出一张链路能力卡：

```text
业务问题与失败后果
→ 输入/成功终态/失败终态
→ 编排与状态机制
→ Tool/RAG 与副作用边界
→ 评测/观测方式
→ 为什么是亮点（解决什么生产级问题，付出什么代价）
→ 适合融合的业务对象与生命周期
→ 目标项目源码嵌入点和最小重实现
```

## 源码门禁

扫描器只负责定位候选。每条最终链路必须回读真实源码正文，核对实际入口、调用关系、状态/副作用和输出；不得只根据类名、文件名、关键词、装饰器或 README 写结论。至少收集 5 个本地证据点并覆盖 3 个链路段，否则标 `[候选链路]` 或 `[待确认]`。

用户讲解遵循 [证据优先与精简讲解](../../references/evidence-first-explanation.md)：主文讲业务链路、机制、失败边界和证据 ID，不大量粘贴代码或罗列类；完整路径、行号、符号和最小摘录放证据附录。

## 扫描入口

- API/CLI/worker：FastAPI、Flask、Django、websocket、命令行和队列消费者。
- Agent 编排：LangGraph、LangChain、CrewAI、AutoGen、MCP 或自研 graph/orchestrator。
- Tool：tool 装饰器、MCP server、函数 schema、插件注册表。
- 长程任务：Celery、RQ、Arq、Temporal、Prefect、Airflow、async task、checkpoint/store。
- RAG/记忆：ingestion、retriever/reranker、向量库、conversation store、摘要/记忆管理。
- 评测/观测/安全：eval dataset、grader、trajectory、trace、token/cost、权限、审计和 sandbox。

## 解释规则

输出“业务入口 → 编排/状态 → 模型决策 → Tool/RAG → 持久化/副作用 → 评测/观测 → 用户交付”。最多按证据追 4 层；不能执行用户代码、导入项目模块或深挖第三方依赖。无法确认的调用标 [待确认]。

主文解释每条亮点时必须同时写：

1. **解决的问题**：为什么普通 API、规则或单次 LLM 调用不够；
2. **工程机制**：状态、可靠性、安全、评测、记忆或观测中真正改变了什么；
3. **失败边界**：异常、重复、越权、过期知识、成本超限时如何处理；
4. **业务融合**：哪个业务对象天然需要该机制，目标项目中准备放在哪个源码入口；
5. **证据与边界**：证据 ID、个人职责和仍需完成的改造。

不要把类名列表当作亮点解释。类名只在证明模块边界或关键取舍时出现，完整路径、行号和最小摘录放到证据附录。

扫描时读取 [高价值 Agent 链路](../../references/high-value-agent-chains.md)、[证据协议](../../references/evidence-protocol.md) 和 [输出结构](../../references/output-schema.md)。只有发现未知框架或模式时才读取 [动态规则更新](../../references/dynamic-rule-update.md)，生成 candidate_patterns 和 rule_update_proposal，不自动改稳定规则。
