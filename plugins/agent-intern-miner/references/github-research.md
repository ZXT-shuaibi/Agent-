# GitHub 与公司公开资料研究

## 研究顺序

1. 先查官方公司页面、岗位描述、公开产品/技术文章和 GitHub 组织。
2. 先从用户事实或链路报告抽象 `internship_chain`，再按承载业务背景和链路嵌入点搜索，不以曼弗业务相似度作为必要条件。
3. 再查可信招聘平台、作者文档和仓库 issue/release。
4. 搜索摘要只做定位；不能用摘要证明源码能力或公司内部事实。

每条外部事实记录 url、accessed_at、source_type、confidence。查不到曼弗科技的公开业务或技术信息时写“未知”，只给通用场景建议。

## 候选池

搜索覆盖多个业务域（研究/报告、客服/工单、问数/数据分析、企业知识、DevOps）和多个热度区间。star 只是弱信号；达到约 1k 可作为社区验证，超过后不再显著加分。避免只用 sort=stars。

候选字段：name、url、stars、updated_at、license、readme_probe、domain_bucket、engineering_signals、risk_flags、internship_chain、carrier_scenario、business_object、lifecycle、chain_insertion_point、carrier_fit、saturation_risk、query、accessed_at。

README probe 只能判断项目类型（业务系统、框架、SDK、桌面壳、工具链）和候选定位，不能支撑最终“负责功能/技术难点”或“链路已成功承载”。

## 确认与验证门禁

- 先展示 3–4 个短名单、选择理由、主要淘汰理由和“实习链路 → 业务载体”的映射，等待用户确认技术栈/方向。
- 确认后才调用拉取脚本；脚本失败、源码不可读或证据少于 5 个，直接淘汰。
- 只依据本地源码 manifest 写“已有能力”。开源项目默认作为独立项目或改造练习；除非用户提供真实参与证据，否则不能写成曼弗科技实习成果。
