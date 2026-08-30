---
name: agent-intern
description: Use when a user needs Python/LLM/Agent internship chain discovery, Agent project selection, or evidence-safe resume packaging.
---

# Agent 实习挖掘总入口

> 内部 ID：`agent-intern`

## 作用

总入口只做两件事：判断你手上的材料属于哪一种情况，以及把任务交给正确的下游模块。它不直接扫描源码，也不替你编造链路结论。

## 输入

- Python/Agent 项目目录、仓库或压缩包；
- 只有文字形式的实习/项目工作记录；
- 已有链路报告、简历 bullet 或面试问题；
- 想寻找 GitHub 参考项目的业务方向。

## 输出

给出下一步模块、需要补充的材料和推荐执行顺序；完整流程为“扫描/提取 → 项目筛选（可选）→ 包装 → 拷打 → 门禁”。

## 何时使用

当你不确定该从源码、口述记录、GitHub 项目还是简历表达开始时使用。已经明确要做某一项时，可以直接调用对应模块。

## 怎么用

直接说：“我有一个 Python Agent 仓库，帮我找最有含金量的实习链路。”如果想跳过路由，可直接说：“使用 `agent-chain-scan` 扫描 `C:\\work\\my-agent`。”

这是独立于 Java bian-intern 的 Agent 领域路由器。只判断用户已有材料和下一步，不直接替用户编写链路结论。

## 路由

| 用户材料/目标 | 路由 |
|---|---|
| Python/Agent 源码、仓库、压缩包 | agent-chain-scan |
| 只有口述工作记录 | agent-chain-extract |
| 想找真实 GitHub Agent 业务项目 | agent-project-select |
| 已有源码证据/链路报告，想写项目经历 | agent-package |
| 已有 bullet，担心被问穿 | agent-grill |
| 拷打高危问题已修补 | agent-self-check |

不要把 Java Controller 规则带入；不要因缺少抽象模式而阻塞，只有目标公司/真实性边界会改变结果时才一次问一个关键问题。

## 推荐路径

~~~text
公司/岗位公开信息 → agent-chain-scan 或 agent-chain-extract
→ agent-project-select（可选）→ agent-package → agent-grill → agent-self-check
~~~

总入口不要一次加载全部 reference。进入具体模块后，由该模块按需读取对应材料：扫描读取链路与证据规则，项目选择读取承载背景与 GitHub 规则，包装读取讲解与输出规则。每个结论都要标来源，开源项目和建议改造不得写成未证实的实习成果。
