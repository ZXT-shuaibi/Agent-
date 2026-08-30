# Agent 实习链路工作台

这是一个可直接从 GitHub 安装的 Codex marketplace，提供面向 Python/LLM/Agent 岗位的实习链路挖掘、源码证据扫描、业务承载项目筛选和面试包装能力。

## 从 GitHub 安装到 Codex

前置条件：本机已安装 Codex CLI，并且 `codex plugin --help` 可以正常执行。公开仓库可以直接读取；只有扫描你自己的私有源码时，才需要额外的 Git 凭据。

在 PowerShell 或终端执行：

```powershell
codex plugin marketplace add ZXT-shuaibi/Agent- --ref main
codex plugin add agent-intern-miner@agent-intern-github
codex plugin list --marketplace agent-intern-github
```

安装完成后新建一个 Codex 任务，让插件重新加载。然后可以直接说：

```text
使用 Agent 实习链路工作台。
扫描 D:\project\my-agent，重点分析长程任务、Tool 稳定性、评测、记忆和 RAG 权限。
```

## 更新和卸载

更新 marketplace 快照并重新安装插件：

```powershell
codex plugin marketplace upgrade agent-intern-github
codex plugin remove agent-intern-miner@agent-intern-github
codex plugin add agent-intern-miner@agent-intern-github
```

卸载插件和 marketplace：

```powershell
codex plugin remove agent-intern-miner@agent-intern-github
codex plugin marketplace remove agent-intern-github
```

## 仓库结构

```text
Agent-/
├── marketplace.json
├── README.md
└── plugins/
    └── agent-intern-miner/
        ├── .codex-plugin/plugin.json
        ├── skills/
        ├── references/
        ├── scripts/
        └── tests/
```

插件的完整中文使用说明、7 个模块的作用、渐进式披露和证据优先规则，见 [插件 README](plugins/agent-intern-miner/README.md)。

## 本地开发安装

如果已经克隆本仓库，也可以把本地 checkout 作为 marketplace：

```powershell
git clone https://github.com/ZXT-shuaibi/Agent-.git
codex plugin marketplace add .\Agent-
codex plugin add agent-intern-miner@agent-intern-github
```

本仓库只负责插件分发和规则实现。插件不会把开源项目或建议改造冒充成曼弗科技实习成果；源码结论必须回读真实代码，所有指标和个人职责都要有可追溯来源。
