# Skill 注册与调用层

33 个 Skill 的唯一正文位于 `../skills/<skillId>/SKILL.md`；知识库只登记元数据和映射，不复制全文。查询先走 `vgame-knowledge-router`，再按 `mappings/question-to-skill.json` 与 `mappings/system-to-skill.json` 加载最小 Skill 和知识包。

注册字段覆盖 skillId、分类、职责、触发条件、输入、输出、覆盖系统、依赖 Skill、证据来源、交付门禁和版本状态。
