# 输出结构

## 扫描报告 JSON

~~~json
{
  "schema_version": "1.0",
  "root": "...",
  "frameworks": [],
  "entrypoints": [],
  "evidence": [{"id": "E1", "path": "...", "line": 1, "symbol": "...", "kind": "orchestration", "excerpt": "...", "confidence": 0.8}],
  "chains": [{
    "name": "...",
    "level": "S|A|B",
    "business_problem": "...",
    "failure_consequence": "...",
    "why_high_value": "...",
    "mechanisms": [],
    "failure_boundaries": [],
    "evidence_ids": [],
    "carrier_fit": [],
    "minimal_reimplementation": "...",
    "measures": []
  }],
  "target_business": "",
  "carrier_mapping": [{"internship_chain": "...", "carrier_scenario": "...", "business_object": "...", "lifecycle": "...", "chain_insertion_point": "...", "minimal_reimplementation": "...", "claim_level": "independent_project|suggested_change|not_writable"}],
  "candidate_patterns": [],
  "rule_update_proposal": null
}
~~~

## 项目推荐包

~~~markdown
# 推荐结论
## 候选池与淘汰理由
## 本地源码证据（E1...）
## 已有能力 [源码证据]/[用户事实]
## 建议改造 [建议改造]
## 完成后可写
## 当前不可写 [不可写成已完成]
## 业务场景与个人最小负责模块
## 方案演进 A → B → C
## 简历 bullet 与证据 ID
## Agent 专属追问与数据来源
## rule_update_proposal（如有）
~~~

## 链路能力卡（Markdown 必须逐条解释）

每条重点链路不能只输出名称和技术栈，至少包含：

| 字段 | 内容 |
|---|---|
| 业务问题/失败后果 | 谁的什么任务会因失败而损失、逾期、越权或返工 |
| 为什么是亮点 | 为什么普通 API、Prompt 或单次调用解决不了；方案代价是什么 |
| 工程机制 | 状态、checkpoint、Tool schema、权限、评测、记忆或 trace 的具体作用 |
| 失败边界 | 超时、脏数据、重复、过期、越权、成本超限时的行为 |
| 源码证据 | 至少 5 个路径/行号/符号，覆盖至少 3 段链路 |
| 业务融合 | 业务对象、生命周期、天然副作用及目标项目源码嵌入点 |
| 最小重实现 | 用户真正需要改的模块、测试、日志或评测，不把建议写成完成 |
| 可衡量结果 | 指标名称、数据来源和基线；无来源时写待测量/估算 |

Markdown 主文只放结论、机制、边界和证据 ID；完整路径、行号和摘录放证据附录，不用大量代码和类名替代解释。

所有报告带 generated_at、source_labels、confidence；Markdown 是面向用户的主文档，JSON 是脚本和后续 skill 的交接格式。
