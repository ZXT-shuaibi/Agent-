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
- 无法由源码确认的部分标为 `[待确认]`。

## 何时使用

你能提供源码，并且希望知道“真正能写进项目经历的工程链路”时使用。没有源码时改用 Agent 口述链路提取。

## 怎么用

说：“使用 `agent-chain-scan` 扫描 `C:\\work\\my-agent`，重点看长程任务、Tool 可靠性和评测。”插件会先运行 [源码扫描器](../../scripts/scan_agent_repo.py)，再基于本地证据解释业务价值。

从 Agent 能力入口切入，不寻找 Java Controller。先运行源码扫描器，再只对本地证据做业务解释。

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

扫描时读取 [高价值 Agent 链路](../../references/high-value-agent-chains.md)、[证据协议](../../references/evidence-protocol.md) 和 [输出结构](../../references/output-schema.md)。只有发现未知框架或模式时才读取 [动态规则更新](../../references/dynamic-rule-update.md)，生成 candidate_patterns 和 rule_update_proposal，不自动改稳定规则。
