# CHG-026：预览等级角标与随机主材前置

仅增量修改06映射装备的Items、UIlevel与配置清单。无需改客户端或Drop；保留CHG-025等最新候选数据。不得运行旧整包生成器覆盖当前06。

## 规则与入口

- `rules.mjs`：纯函数`previewPatches(books, sources)`，返回具名字段对应的单元格变更与73条等级链。重复应用返回零变更；缺失CHG-019道具、U列冲突或4375等级/品质不符时拒绝执行。
- `prepare.py`：只读提取完整行宽、公式、实际开箱源，记录全部22份候选和4份相关SVN文件哈希。禁止覆盖已存在的本次基线。
- `update.mjs --inspect`：只渲染原表；`update.mjs`：使用artifact-tool备份、修改、渲染并导出三份暂存。追加U列，不移动前20列。
- `validate.py`：独立从首通Drop→实际Items.ParaList→Generate推导首通等级；常规按正概率等级和品质重新验算分配。逐格保护其他数据与公式，验证150行首次/重复预览与其他候选、SVN哈希。
- `publish.ps1 -VisualQaApproved`：所有图片经执行者复核后使用；必须通过暂存校验，并同时持有三文件独占锁、核对基线/备份/暂存哈希，才可替换。失败回滚已写文件，不关闭Excel。
- `validate.py --final`：重读实际06并写正式验算报告；`update.mjs --check-current`：以当前文件运行纯函数，预期零待修复项。

运行时必须由`load_workspace_dependencies`取得绑定Python、Node和node_modules，用当前目录junction接入artifact-tool；不得使用其他库写XLSX。正式编辑前按Spreadsheets技能登记一次操作，预期输出3份。

顺序：prepare → node --test rules.test.mjs → inspect并看图 → 编辑登记 → update → validate → 全部页签范围看图 → publish → validate --final → check-current。

本次快照冻结用于重现验证；不要删除它来跳过并发检查。今后新基线应另建独立运行目录、保留本次备份与验算记录。完整生产重建须在CHG-019～025规则已恢复并核验后，将`previewPatches`作为末端增量步骤应用；若前置道具或开箱规则不满足则停止，不能降级恢复旧预览。纯函数的幂等性不代表可以重复覆盖已发布文件。

首通等级替代数量角标是用户已确认行为；4375是实际箱，导入后其他复用通用PropItem的位置同样受影响。本次不导表、不做游戏内截图、不代替用户最终验收。
