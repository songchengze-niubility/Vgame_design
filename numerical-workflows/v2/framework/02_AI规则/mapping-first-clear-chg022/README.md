# CHG-022：4375实际首通箱闭环

用户确认第三层固定开出10级金装。只修06候选，不写SVN。

运行顺序：绑定Python执行`prepare.py`只读提取和哈希；绑定Node执行`update.mjs --inspect`看原表；按Spreadsheets技能登记编辑后执行`update.mjs`，输出暂存五文件；`validate.py`独立验证发奖、身份、开箱、预览、常规引用及保留字段。检查所有渲染后，核对全部候选和暂存哈希、排除Excel锁定，统一替换五文件；repair.json存为05验算目录`mapping-equip-first-clear-CHG022.json`，再执行`validate.py --published`验证实际交付。

`prepare.py`预期CHG-021候选：第三层仍发4212、候选Generate尚无4375。不得在已发布CHG-022上重复执行，不绕过断言。旧P02重建链须再应用CHG-019→020→021→022；新P02重新生成后须重审各增量基线。CHG-021旧验证器不认识4375实际箱例外，不能用其覆盖当前业务规则，也不能把检查失败简单改成通过。

Python仅用于读取与验证，XLSX全部由artifact-tool导入编辑导出；node_modules为绑定依赖目录的junction。常规45个缺失正式Item、120条正式旧预览保留在报告的formalUnchangedGaps中，与本次候选验收分开。
