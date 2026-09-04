# CHG-023 稀有增伤池

只修改`06_最终配置/映射装备`中的SpecialEquipment、SpecialEquipmentEffect、SpecialEquipmentEffectDrop及00_配置清单，禁止写正式Datas。

规则源：`rules.json`及`03_沉淀MD/养成/映射装备稀有增伤词条六档-CHG023-2026-08-27.md`。

首次增量执行顺序：使用工作区依赖中的Python运行`preflight.py <用户映射装备.xlsx>`（环境变量VGAME_CONFIG_DATAS指向正式源，只读）；用已配置artifact-tool依赖的Node运行`update.mjs --inspect`并检查样式；完成表格技能要求的编辑标记后运行`update.mjs`；最后运行`validate.py`。此增量入口为一次性补丁，已存在受控ID时预检会拒绝，避免覆盖并发或用户后续编辑。

持续生产：基础生成器已导入相邻`mapping_rare_rules.py`。纯数据生成可幂等重放；不需要在每次基础生产后再次跑这个一次性补丁。基础生成的其他流程仍遵循原有各项增量门禁。

验收：专项840项通过；全量属性检查35/36通过。未通过项为本次前已经存在的10条红装Name=`待占位`与正式名称不同，本次不处理。所有未涉及的06文件及正式源文件Hash不变。
