# 输出结构

## 扫描报告 JSON

~~~json
{
  "schema_version": "1.0",
  "root": "...",
  "frameworks": [],
  "entrypoints": [],
  "evidence": [{"id": "E1", "path": "...", "line": 1, "symbol": "...", "kind": "orchestration", "excerpt": "...", "confidence": 0.8}],
  "chains": [],
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

所有报告带 generated_at、source_labels、confidence；Markdown 是面向用户的主文档，JSON 是脚本和后续 skill 的交接格式。
