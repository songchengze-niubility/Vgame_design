# Vgame 驾驭工程入口

本目录属于 `Vgame_design` Git 仓库，负责 Vgame 策划 Agent 的安装、路径配置、更新、检查和启动。

1. 将上级目录 `${VGAME_DESIGN_ROOT}` 视为策划知识、Skill、流程和知识图谱的权威来源。
2. 将本机配置中的 `${VGAME_ROOT}` 视为真实 Vgame SVN 工程，只在用户明确授权后写入。
3. 首次使用或更换电脑时运行 `配置本机路径.bat`，随后运行 `一键安装.bat`。
4. 新建 Codex 对话时直接打开 `${VGAME_DESIGN_ROOT}`，由上级 `AGENTS.md` 路由到项目 Skill 和 SVN 工程。
5. 不要在 SVN 工程中复制本目录、Skill 或知识图谱，避免 Git 与 SVN 出现两份驾驭工程。
