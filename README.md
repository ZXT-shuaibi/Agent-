# agent-intern-miner

面向 Python/LLM/Agent 岗位的独立实习链路挖掘插件。它与 Java `bian-intern` 并列，不加载 Spring Controller 规则，也不修改原插件。

## 安装到 Codex

### 前置条件

- Codex CLI 能执行 `codex plugin --help`；
- 需要扫描或拉取源码时，本机有 Python 3 和 Git；
- 插件目录必须完整保留 `.codex-plugin/`、`skills/`、`references/` 和 `scripts/`，不要只复制单个 `SKILL.md`。

推荐使用随交付物提供的本地 marketplace 包。解压后目录应为：

```text
agent-intern-marketplace/
├── marketplace.json
└── plugins/
    └── agent-intern-miner/
        ├── .codex-plugin/plugin.json
        ├── skills/
        ├── references/
        └── scripts/
```

在 PowerShell 或终端执行：

```powershell
codex plugin marketplace add "D:\1\agent-intern-marketplace"
codex plugin add agent-intern-miner@agent-intern-local
codex plugin list --marketplace agent-intern-local
```

路径替换为实际解压目录。安装后新建任务，让 Codex 重新发现插件；旧任务不会保证自动获得新 skill。

更新本地包时，替换 marketplace 目录中的插件版本，再执行：

```powershell
codex plugin remove agent-intern-miner@agent-intern-local
codex plugin add agent-intern-miner@agent-intern-local
```

卸载时执行：

```powershell
codex plugin remove agent-intern-miner@agent-intern-local
codex plugin marketplace remove agent-intern-local
```

Codex Desktop 若提供插件管理界面，可以从界面查看安装结果；CLI 是本 README 的确定性安装路径。插件结构可参考 [OpenAI Codex plugin structure](https://developers.openai.com/codex/plugins/build#plugin-structure)。

## 其他平台使用

### 支持 Agent Skills / `SKILL.md` 的平台

保持整个 `agent-intern-miner` 目录不变，把 `skills/` 注册为 skill 搜索目录，并以 `skills/agent-intern/SKILL.md` 作为总入口。平台路由到子 skill 后，只读取该文件明确指向的 reference；相对路径已经按完整插件目录组织。

平台还需要允许：

- 读取待分析的本地源码；
- 执行 Python 脚本；
- 在用户确认 GitHub 短名单后执行 Git 拉取；
- 写入扫描报告、manifest 和最终 Markdown。

如果平台只能导入单个 skill，不要把 7 个 skill 全塞进一个系统提示词。先加载 `agent-intern`，由它选择 `agent-chain-scan`、`agent-project-select` 等子模块，再提供对应 reference。

### 不支持 skill 目录的平台

把下面这段作为项目级或系统级入口说明，并让平台能够访问完整插件目录：

```text
先读取 <插件根目录>/skills/agent-intern/SKILL.md。
只加载路由到的一个子 SKILL.md，以及该文件明确要求的 reference。
运行脚本时使用 <插件根目录>/scripts；不要一次加载全部文档。
```

不具备文件读取、Git 或命令执行能力的纯聊天平台，不能完成“源码已验证”的链路扫描和 GitHub 项目验证。它只能处理用户上传的片段、口述链路、简历包装和面试拷打，输出必须标 `[待确认]`，不能声称读过完整源码。

## 解决什么问题

Agent 项目很容易被写成“调用模型、接入 RAG、封装几个 Tool”。本插件从业务闭环和工程证据出发，优先识别：

- 长程任务、持久化状态、checkpoint、恢复/续跑和幂等；
- Tool schema、权限、超时、重试、熔断、沙箱和副作用补偿；
- 评测数据集、轨迹、回归、事实性、工具成功率、成本和延迟；
- 记忆生命周期、上下文压缩、来源、隔离和删除；
- 多 Agent/人机协同、可观测性、模型路由和安全治理。

项目筛选不要求 GitHub 项目和曼弗业务相同。插件会把曼弗实习作为真实链路来源，把 GitHub 项目作为更适合简历的业务承载背景，再检查链路能否在承载项目中自然重实现。合规证据链、合同履约、指标口径治理、研发变更风险、知识变更发布和跨系统异常处置优先于通用聊天、会议纪要和单次报告生成。

## 完整使用流程

```text
agent-intern
  → agent-chain-scan / agent-chain-extract
  → agent-project-select（需要 GitHub 项目时）
  → agent-package
  → agent-grill
  → agent-self-check
```

### 第 0 步：准备输入

最小输入模板：

```text
实习业务：可脱敏描述
我实际做过：
可提供的源码/目录：
不能公开的内容：
希望强化的 Agent 能力：
目标岗位：
可投入改造时间：
```

### 第 1 步：进入总入口

```text
使用 agent-intern。先判断我的材料应该走源码扫描还是口述提取，
不要直接生成简历，也不要假设曼弗业务或个人职责。
```

### 第 2 步：提取真实链路

有源码：

```text
使用 agent-chain-scan 扫描 D:\project\my-agent。
重点检查长程任务、Tool 可靠性、评测、记忆和 RAG 权限。
扫描器命中后必须回读真实源码，再形成最终链路。
```

没有源码：

```text
使用 agent-chain-extract。我先列出做过的事情，你一次只问一个问题。
没有源码的结论只标用户事实或待确认。
```

### 第 3 步：选择经历承载项目

先把上一步链路报告交给 `agent-project-select`：

```text
根据这份曼弗实习链路报告，寻找 3–4 个业务背景不烂大街、
能够自然承载这些链路的 Python Agent 项目。
先给短名单、链路嵌入点和淘汰理由，不要先拉取源码。
```

看到短名单后回复“确认 1、3”或“全部”。只有确认后，插件才拉取仓库、生成 manifest 并回读真实源码。搜索摘要、star 和 README 只能筛候选，不能证明设计亮点。

### 第 4 步：形成项目表达

```text
使用 agent-package。基于链路报告和源码证据生成项目表达。
主文只讲业务链路、关键机制、失败边界和证据 ID；
路径、行号、符号和最小代码摘录统一放证据附录。
```

### 第 5 步：拷打与门禁

```text
使用 agent-grill，一次只问一个问题，检查状态恢复、Tool 副作用、
权限、评测、记忆、成本、指标来源和个人角色。

高危问题修复后，使用 agent-self-check 做最终门禁。
```

## 证据优先，讲解精简

查找设计亮点和核心链路必须基于真实代码。`scan_agent_repo.py` 只负责定位候选，最终结论还必须读取本地源码正文并确认实际调用关系。类名、文件名、装饰器、关键词或 README 都不能单独作为结论。

每个源码型最终项目至少需要 5 个证据点，并覆盖入口、编排/状态、Tool/RAG/副作用、评测/观测中的至少 3 段。

面向用户的主文不大量堆叠代码和类，推荐结构是：

```text
一句话结论
→ 业务链路图
→ 2–4 个关键设计及解决的问题
→ 失败边界和方案取舍
→ 证据 ID
```

完整代码定位放“证据附录”：证据 ID、路径、行号、符号、链路位置、最小摘录和可信度。详细规则见 [证据优先与精简讲解](references/evidence-first-explanation.md)。

## 渐进式披露

| 层级 | 默认加载内容 | 什么时候继续加载 |
|---|---|---|
| 1. 插件发现 | `plugin.json`、`agents/openai.yaml` | 判断是否属于 Agent 实习/项目任务 |
| 2. 总入口 | `agent-intern/SKILL.md` | 根据用户材料路由到一个子 skill |
| 3. 子 skill | 当前任务对应的一个 `SKILL.md` | 子 skill 明确要求某份 reference 时 |
| 4. 专项 reference | 证据、业务承载、GitHub、输出或动态规则中的一部分 | 当前阶段确实需要时 |
| 5. 脚本和源码 | 扫描器、搜索器、拉取器及候选项目源码 | 得到用户授权并进入执行阶段时 |

总入口禁止一次加载全部 reference。扫描、项目选择、包装、拷打和门禁彼此独立；不执行的阶段不会加载其详细规则。

## 7 个模块对照表

内部 ID 必须使用英文小写和连字符，方便 Codex 自动发现；下面的中文名是你在使用时应记住的名称。

| 中文名称 | 内部 ID | 作用 | 什么时候用 | 你需要提供 | 主要产出 |
|---|---|---|---|---|---|
| Agent 实习挖掘总入口 | `agent-intern` | 判断当前材料并选择下一步 | 不知道先做什么，或要完整走一遍 | 任意项目/实习目标和已有材料 | 路由建议与执行顺序 |
| Agent 源码链路扫描 | `agent-chain-scan` | 从 Python/Agent 源码定位端到端链路 | 有仓库、源码目录或压缩包 | 本地项目路径 | 扫描 JSON、证据点、候选链路 |
| Agent 口述链路提取 | `agent-chain-extract` | 从工作记录还原真实业务链 | 没有可读源码，只有做过的事情 | 按问答提供工作记录 | 事实链、个人负责范围、缺口 |
| GitHub Agent 项目筛选 | `agent-project-select` | 找业务型项目并拉取源码验证 | 需要找可包装的真实参考项目 | 方向偏好和候选确认 | 短名单、源码证据、改造方案 |
| Agent 项目/实习包装 | `agent-package` | 把证据写成简历和面试表达 | 已有链路或源码证据 | 链路报告、个人角色、指标来源 | 项目名、bullet、30 秒/2 分钟稿 |
| Agent 面试拷打 | `agent-grill` | 压力测试技术深度和真实性 | 担心被追问、被问穿 | 已写 bullet 或项目报告 | 漏洞清单、补证据问题 |
| Agent 质量门禁 | `agent-self-check` | 在交付前检查证据、角色和可防守性 | 准备投递或定稿 | 完整包装材料 | 通过/警告/高危和修改清单 |

## 怎么调用

可以直接说中文，插件会自动路由；也可以显式写内部 ID。例子：

```text
分析 C:\\work\\my-agent，找出最有含金量的链路
→ 使用 Agent 源码链路扫描（agent-chain-scan）

我只有实习工作记录，没有源码，帮我还原链路
→ 使用 Agent 口述链路提取（agent-chain-extract）

根据这份实习链路找 3 个不烂大街、能自然承载这些设计的项目
→ 使用 GitHub Agent 项目筛选（agent-project-select）

把这份链路报告写成简历项目，并标出不能虚构的地方
→ 使用 Agent 项目/实习包装（agent-package）

拷打这 3 条 bullet，看看面试官会怎么问
→ 使用 Agent 面试拷打（agent-grill）

检查最终版本能不能投递
→ 使用 Agent 质量门禁（agent-self-check）
```

单独使用时不必手动加载前置模块；如果要完整流程，按“总入口 → 扫描/提取 → 项目筛选（可选）→ 包装 → 拷打 → 门禁”执行。

### 项目筛选的两种结果

`agent-project-select` 不只寻找“项目本身很强”的仓库，还支持“经历承载项目模式”：先从曼弗实习提取真实链路，再寻找业务背景更适合简历的公开项目，把链路在该项目中重新实现。曼弗业务是事实来源，GitHub 项目是公开业务载体，二者不能混写。

源码扫描脚本只读取本地文件，不执行用户项目代码；GitHub 项目必须先短名单确认，再真实拉取源码并生成 manifest。README 或 star 不能替代源码证据。

## 真实性边界

所有结论必须标注 `[用户事实]`、`[源码证据]`、`[公开资料]`、`[建议改造]` 或 `[不可写成已完成]`。开源项目和建议改造可以写成独立项目、课程项目或拟实施方案，但不能写成没有真实证据的曼弗科技实习成果。指标没有来源时只能写“待测量/估算”。

## 规则可扩展

扫描到新框架或新模式时先输出 `candidate_patterns` 与 `rule_update_proposal`，满足本地证据、三段链路和非重复条件后再追加版本化规则；不会自动把一次扫描结果写入稳定规则库。
