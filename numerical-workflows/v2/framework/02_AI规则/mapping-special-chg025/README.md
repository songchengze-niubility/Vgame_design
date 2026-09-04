# CHG-025 品质准入与SpecialEffect纠正

取代CHG-024的FixEffect错误落点，规则为用户明确指令：绿蓝紫无RareEffect、非红无SpecialEffect，具名红装通过SpecialEffect单技能池绑定。基础生成器及全量属性验证已同步。不得执行全量生成器清空现有06。

执行：bundled Python `preflight.py` → bundled Node `update.mjs --inspect`并看图 → 按Spreadsheets技能标记一次编辑 → `update.mjs`生成暂存 → `validate.py`并看全部预览 → `publish.ps1`备份、全部独占锁、Hash检查及替换 → `validate.py --final`。仅写06四表，正式工作副本只读。

当前21池均使用同号PoolId/EffectId/SkillId，不是跳过中间表的直接引用。每池EffectList仅为`技能ID,100`。同名双手套共用30602池；虚空突袭之刃为空。Quality表刷新数量不在本次修改范围，不声称特殊效果必定出现。

报告位于05_验算核算/mapping-special-CHG025*.json。最终验证通过后仅清理本目录staged的四份临时xlsx；实际06和备份保留。旧CHG-024写入入口已停用，历史验证报告不再代表当前规则正确性。
