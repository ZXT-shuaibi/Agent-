# Agent 实习链路工作台

这是一个可直接从 GitHub 安装的 Codex marketplace，提供面向 Python/LLM/Agent 岗位的实习链路挖掘、源码证据扫描、业务承载项目筛选和面试包装能力。

仓库地址：[ZXT-shuaibi/Agent-](https://github.com/ZXT-shuaibi/Agent-)

## 完整操作流程

### 第一步：在开发电脑准备并发布仓库

如果你还没有本地副本：

```powershell
git clone https://github.com/ZXT-shuaibi/Agent-.git
cd .\Agent-
```

修改插件或 README 后，检查、提交并推送：

```powershell
git status
git add -A
git commit -m "Describe the change"
git push -u origin main
```

如果 GitHub 尚未保存登录凭据，先执行：

```powershell
gh auth login -h github.com
```

选择 `HTTPS` 和浏览器登录。公开仓库不需要登录即可克隆，但推送修改需要有仓库写权限。

### 第二步：在目标电脑检查 Codex

打开 PowerShell，确认插件命令可用：

```powershell
codex plugin --help
```

如果提示找不到 `codex`，先安装 Codex CLI，再继续下面的步骤。

## 从 GitHub 安装到 Codex

前置条件：本机已安装 Codex CLI，并且 `codex plugin --help` 可以正常执行。公开仓库可以直接读取；只有扫描你自己的私有源码时，才需要额外的 Git 凭据。

在 PowerShell 或终端执行：

```powershell
codex plugin marketplace add ZXT-shuaibi/Agent- --ref main
codex plugin add agent-intern-miner@agent-intern-github
codex plugin list --marketplace agent-intern-github
```

三个命令的作用分别是：添加 GitHub marketplace、安装其中的 `agent-intern-miner` 插件、检查插件是否可见。安装完成后新建一个 Codex 任务，让插件重新加载。然后可以直接说：

```text
使用 Agent 实习链路工作台。
扫描 D:\project\my-agent，重点分析长程任务、Tool 稳定性、评测、记忆和 RAG 权限。
```

### 第三步：确认已安装

```powershell
codex plugin list --marketplace agent-intern-github --json
```

输出中应能看到 `agent-intern-miner`。如果当前 Codex 任务没有识别新 skill，关闭后新建任务；插件安装不会保证旧任务实时刷新。

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

### 常见问题

- `marketplace.json not found`：检查 `codex plugin marketplace add` 使用的是仓库根目录，不能指向 `plugins/agent-intern-miner`。
- `plugin not found`：先运行 `codex plugin list --available --marketplace agent-intern-github`，确认 marketplace 快照能看到 `agent-intern-miner`。
- 修改后仍是旧版本：运行更新命令，或先移除插件再重新添加；然后新建 Codex 任务。
- `git push` 要求用户名密码：不要填写 GitHub 登录密码，使用 `gh auth login -h github.com` 或 Personal Access Token 完成 Git 凭据配置。
- 私有仓库无法拉取：目标电脑需要 GitHub 读权限，并确保 `gh auth status` 显示登录有效。

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

## 生成 bian-intern 风格的独立压缩包

如果你希望像 `bian-intern-plugin.zip` 一样拿到一个单独插件目录，可以从仓库根目录运行：

```powershell
python .\scripts\build_standalone_plugin.py `
  --output .\dist\agent-intern-plugin-v1.1.0.zip
```

压缩包内容为：

```text
agent-intern-miner/
├── .codex-plugin/plugin.json       # Codex manifest
├── .claude-plugin/plugin.json      # Claude Code 兼容 manifest
├── agents/
├── profiles/
├── references/
├── scripts/
├── skills/
└── README.md
```

它只包含运行所需的插件文件，不包含 `.git`、测试目录、`__pycache__` 或 `.pyc`。插件规则仍以 `plugins/agent-intern-miner/` 为唯一来源，重新运行脚本即可生成最新 zip，避免手工复制造成版本分叉。

### 如何同步到 GitHub

推荐把本仓库根目录同步到 GitHub，因为根目录的 `marketplace.json` 可以让 Codex 直接安装：

```powershell
git add -A
git commit -m "Update Agent internship workbench"
git push origin main
```

如果要分发独立 zip，可以把生成的 `dist\agent-intern-plugin-v1.1.0.zip` 上传到 GitHub Release 的 Assets，或作为仓库附件保存。不要把 `dist/` 的生成文件反向复制进插件源码目录。

### 独立 zip 怎么安装

- **Codex**：优先使用本仓库的 GitHub marketplace 安装命令。Codex 的 `plugin add` 需要 marketplace 条目；单独 zip 解压后如果要作为本地 marketplace 使用，需按根目录 `marketplace.json` 的结构放入 `plugins/agent-intern-miner/`。
- **Claude Code 或支持插件目录的平台**：解压后，将 `agent-intern-miner/` 放入平台的插件/skills 目录；压缩包内的 `.claude-plugin/plugin.json` 用于识别插件，`.codex-plugin/plugin.json` 保留 Codex 元数据。
- **只支持单个 `SKILL.md` 的平台**：读取 `agent-intern-miner/skills/agent-intern/SKILL.md` 作为入口，并保留同级 `references/`、`scripts/` 和其余 skills，不能只复制一个文件。

## 本地开发安装

如果已经克隆本仓库，也可以把本地 checkout 作为 marketplace：

```powershell
git clone https://github.com/ZXT-shuaibi/Agent-.git
codex plugin marketplace add .\Agent-
codex plugin add agent-intern-miner@agent-intern-github
```

本仓库只负责插件分发和规则实现。插件不会把开源项目或建议改造冒充成曼弗科技实习成果；源码结论必须回读真实代码，所有指标和个人职责都要有可追溯来源。
