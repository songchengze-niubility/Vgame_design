# 映射之匙与任务06增量

一次性受控落表批次`KEY-TASK-20260827`。不写SVN，不重建整套映射装备。

> 原批次9条日周解锁改动已被用户否决，由`CHAPTER-CORRECTION-20260827`撤回。原prepare/update/publish已加纠偏后重跑保护。当前只读验收用 `correct_chapter.py validate --published`；不要按旧验证的123/140结论重新改表。

- `read_snapshot.py`只读提取候选；`prepare.py`按语义ID定位修改、备份和哈希。
- `update.mjs`使用bundled artifact-tool导入、局部编辑、渲染和导出暂存。
- `validate.py`独立检查数量、任务/解锁/掉落链与未改字段；`--published`复读实际06。
- `prepare_reports.py`刷新本轮验收报告，旧整包报告仅留历史。
- `publish.ps1`统一取得写锁、核对哈希、写入并支持失败回滚。

工作记录与备份：`../../05_验算核算/映射之匙任务_20260827/`。本轮已发布，不可不经新基线审核直接重跑prepare或publish。原`validate.py`保留历史规则，不作为当前Task验收入口。

DropId必须从业务节点回查。第二章36星是11000012，不是文档曾误写的11000011。读取Drop的ID公式须使用缓存解析业务引用，写入时原样保留公式。

纠偏工具：`correct_chapter.py`按当前Jottings链核对章节，先确认Task仅有18格误改，再将误改前Task备份完整恢复；`correct_chapter.mjs`用artifact-tool补任务清单落点及正确56组/69条数量；`publish_chapter.ps1`在全文件写锁及哈希一致后发布。记录：`../../05_验算核算/章节任务纠偏_20260827/`。章节配置本身已存在06，本次零新增章节任务；映射奖励各25×3、共18把一次性。资源类型计数、周最高分和入池刷新仍是程序验收门禁，静态通过不代表运行通过。

正文同步：用户确认06当前配置正确后，`sync_chapter_md.py sync`只读06并更新章节沉淀MD的完整正文，旧正文归档至`../../05_验算核算/章节任务MD同步_20260827/`；不会写Excel。已执行一次，后续只读复核用`sync_chapter_md.py validate`。核验总表、奖励矩阵、69条明细与一次性汇总，同时保护06及相关SVN源表哈希。
