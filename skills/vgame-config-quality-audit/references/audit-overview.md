# 配置质量审查总览

`vgame-config-quality-audit` 是 Vgame 的配置 QA 层。

它回答：

```text
这批配置是否存在断引用、错源表、错字段、错 ID、展示与真实奖励不一致、导出/注册风险？
```

## 定位

它是验收器，不是设计器。

| 不做 | 交给 |
|---|---|
| 奖励价值和经济合理性 | `senior-game-economy` / `game-numerical-analysis` |
| Drop/UIlevel 奖励落地 | `vgame-reward-drop-sync` |
| ItemId 产销意义 | `vgame-economy-source-map` |
| LevelId/Unlock/SystemOpen 进度链 | `vgame-level-progression-map` |
| schema、导表、生成物溯源 | `vgame-config-schema` |

## 审查层级

1. 源表层：是否改对源 Excel，是否误用生成 JSON。
2. 注册层：是否在 `__tables__.xlsx` 中注册，输入文件是否存在。
3. schema 层：表头、字段、复合类型和枚举是否可解释。
4. 引用层：ItemId、DropId、RewardId、LevelId、Unlock/SystemOpen 是否闭环。
5. 奖励层：真实奖励引用与 UI 展示字段是否混淆。
6. 风险层：付费、抽卡、活动、双倍、邮件、排行等高风险引用是否标记。

## 审查原则

- 只读优先。
- 源 Excel 优先，生成 JSON 只作导出物或运行证据。
- 不按 `Drop.IsValid` 判断 Drop 行有效性。
- 已知历史基线要标注，不要当成新改动造成的问题。
- 脚本发现的是结构风险，最终业务判断仍需对应专项 skill。
