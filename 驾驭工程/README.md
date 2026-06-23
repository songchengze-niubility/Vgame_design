# Vgame 驾驭工程启动入口

## 定位

本目录随 `Vgame_design` Git 仓库统一分发，负责安装、配置、更新、检查和启动。真实游戏工程仍由 SVN 管理，通过每台电脑自己的 `${VGAME_ROOT}` 路径访问。

## 权威来源

| 内容 | 权威位置 |
|---|---|
| 真实游戏工程、配置、代码和资源 | `${VGAME_ROOT}`，SVN 工作副本 |
| 驾驭工程启动脚本 | 当前 `Vgame_design/驾驭工程/` |
| 设计、提案、任务与 Harness 规范 | `Vgame_design` Git 仓库 |
| Vgame 项目 Skill | `Vgame_design/skills/` |
| 知识图谱与 Dashboard | `Vgame_design/knowledge-graph/` |

Git 地址：`git@code.dobest.com:spark/Vgame_design.git`

## 第一次使用

1. 用 SVN 拉取 Vgame 游戏工程。
2. 用 Git 克隆 `Vgame_design`。
3. 双击 `配置本机路径.bat`，填写自己的 Vgame SVN 路径。
4. 双击 `一键安装.bat`，检查 Python、Skill、Harness 和知识图谱。
5. 用 Codex 打开 `Vgame_design`，直接开始 Vgame 任务。

机器本地路径保存在：

```text
%LOCALAPPDATA%\Vgame\design-harness.env.bat
Vgame_design\local.env.bat
```

这两个文件不会上传，每位成员可以使用不同盘符。

## 日常入口

| 文件 | 用途 |
|---|---|
| `配置本机路径.bat` | 设置 Vgame SVN、原始策划资料和个人输出目录 |
| `一键安装.bat` | 首次安装或修复环境 |
| `打开驾驭工程.bat` | 打开当前 `Vgame_design` Git 仓库 |
| `更新驾驭工程.bat` | 快进拉取 Git 策划仓库更新 |
| `检查驾驭工程.bat` | 执行 Harness 与图谱只读检查 |
| `启动知识图谱.bat` | 启动 UA 知识图谱 Dashboard |
| `查看新人指南.bat` | 打开 `新人上手指南.html` |

## 新建 Codex 对话

Codex 工作目录选择 `Vgame_design`。根目录 `AGENTS.md` 会读取本机路径配置，加载核心项目 Skill，并通过 `${VGAME_ROOT}` 访问真实 SVN 工程。需要手工提醒时使用 `新对话提示词.txt`。

真实 Excel、代码和资源仍按 SVN 流程提交；设计文档、Skill、图谱和驾驭工程按 Git 流程提交。
