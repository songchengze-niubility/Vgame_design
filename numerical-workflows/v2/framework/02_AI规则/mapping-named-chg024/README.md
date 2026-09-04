# CHG-024 红装具名技能增量配置

**已撤回：以下是历史实施记录，不得重放。** 用户明确要求具名技能使用SpecialEffect；FixEffect方案及保护低品质旧池的做法均错误。update.mjs、publish.ps1已停用。当前使用mapping-special-chg025；本目录rules.json保留已确认名称映射并已改为CHG-025语义。

规则为用户已确认的按名称绑定，只写06候选三表。不得运行全量生成器清空06；其纯数据逻辑已同步，其他批次后处理仍需保留。

1. 设置VGAME_CONFIG_DATAS后，用bundled Python运行 `preflight.py <用户设计xlsx>`；只读检查正式源、附件、公式与空闲Id，保存快照。此入口只适用未落CHG-024的基线。
2. 将node_modules junction指向运行时依赖，用bundled Node执行 `update.mjs --inspect` 并看预览。
3. 按Spreadsheets技能仅标记一次编辑操作，再执行 `update.mjs`；artifact-tool只生成staged三表，不直接覆盖06。
4. 执行 `validate.py`；人工查看全部after预览。检查22件红装/21种技能/10个名称、原字段及六档RareEffect、未改候选和正式哈希。
5. 执行 `publish.ps1`：校验暂存和目标哈希、备份、取得全部独占文件锁后替换；任何失败回滚本批已写文件。用户锁定文件时停下，不强制关闭Excel。
6. 执行 `validate.py --final`，检查实际06文件；汇总报告在05_验算核算。未执行正式Datas导表或运行时验证。

Effect编号沿用SkillId，不重排已有行。三组别名在rules.json；虚空突袭之刃留空，两件白色针织劳保手套都绑定30602。旧SpecialEffect随机池保持原样，不用本次配置擅自清理历史池。
