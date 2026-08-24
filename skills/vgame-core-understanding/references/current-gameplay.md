# Current Gameplay Snapshot

This file captures the current confirmed Vgame gameplay understanding based on the user-edited `玩法全景表` and `玩法关系图`.

> Source refresh note (2026-08-17): unlock values explicitly refreshed below come from the current local SVN working copy's `SystemOpen.xlsx -> Unlock.xlsx -> LevelId` chain. They describe the checked working-copy source, not Production/LIVE availability. Older values from the panorama snapshot are retained only where no newer source audit is stated and must be revalidated before use.

## Formal Main Gameplay

### 主线

- default state: always open
- role: story, onboarding, main combat axis
- main output:
  - EXP
  - breakthrough materials
  - star-map materials
  - one-time diamonds
  - one-time gacha tickets

### 资源副本-金币

- unlock: `主线2-4` (working-copy source, refreshed 2026-08-17)
- role: daily gold supply

### 资源副本-角色经验

- unlock: `主线2-4` (working-copy source, refreshed 2026-08-17)
- role: daily character EXP supply

### 资源副本-专武经验

- unlock: `主线2-4` (working-copy source, refreshed 2026-08-17)
- role: daily signature-weapon EXP supply
- lifecycle note: the exclusive-weapon-to-containment migration remains `CONFLICT`; this configured entry does not prove the gameplay is currently LIVE.

### 旅券副本

- unlock: `玩家等级38` (`SystemOpen 206 → Unlock 4106`, working-copy source, refreshed 2026-08-20)
- role: stable equipment-growth gameplay
- note: split into four boss-oriented stages with different pacing and combat style

### 映射装备副本

- unlock: `主线2-10` (working-copy source, refreshed 2026-08-17)
- role: endgame equipment farm
- note: short-loop, high-frequency farming gameplay with loot-burst feel

### 无限挑战

- unlock: `主线3-15` (working-copy source, refreshed 2026-08-17)
- role: endless parkour verification gameplay
- structure: every three stages loop through `normal -> elite -> boss`

### 竞技场（PVPVE）

- unlock: `主线2-7` (working-copy source, refreshed 2026-08-17)
- season: `14 days`
- role: competitive verification gameplay
- note:
  - not direct PvP shooting
  - both players run the same stage
  - uncleared enemies damage the player's base
  - first base to die loses
  - turrets affect base HP and damage taken

### 爬塔

- unlock: `主线3-10` (`SystemOpen 201 → Unlock 4101`, working-copy source, refreshed 2026-08-20)
- season/reset style: `14 days`
- role: hybrid one-time + cyclic vertical progression gameplay

### 大秘境

- unlock: `角色等级37`
- season: `28 days`
- role: multi-environment climbing gameplay
- note: current late-game hardcore verification mode

### BOSS挑战

- unlock: `主线4-15` (`SystemOpen 204 → Unlock 4104`, working-copy source, refreshed 2026-08-20)
- role: one-time boss-difficulty verification gameplay

## Formal Outer-Loop Systems

### 任务

- `章节任务`
- `每日任务`
- `每周任务`

### Growth And Economy Systems

- `抽卡 / 新手卡池`
- `专武抽卡 / 专武系统`：C-001 最新裁决 B 为“专武向收容物迁移，并保留一个大版本兼容迁移期”。该结论仅为 `APPROVED_TARGET / HUMAN_DECISION_CONFIRMED`；兼容期起止版本、数据方案、旧表/入口/投放切换均为 `IMPLEMENTATION_PENDING`。当前工作副本中的专武残留不得写成迁移已完成或 LIVE，详见 SYS-OUT-GR-05 / SYS-OUT-GR-10 与 DC-A。
- `主线扫荡`
- `签到`
- `商店`
- `通行证`
- `邮件`

### Social Systems

- `公会`
- `好友 / 聊天`

## Current Non-Formal Or Deprecated Content

### Deprecated

- `世界boss`
- `能效本`
- `主角装备本 / 宝石本 / 铭文本（铭文已删除）`
- `肉鸽`

### Draft

- `BOSS无限挑战`

## Closed-Loop Understanding

Default progression loop:

`主线`
-> unlocks systems and early growth
-> stable growth gameplay feeds account power
-> outer-loop systems supplement and organize resources
-> verification gameplay checks whether power converts into real performance

## Power Conversion Map

### Mainline-Fed Growth

- `主线`
  -> `角色等级 / 角色突破 / 星盘 / 阵容扩充`
  -> affects `base stats, skill growth, roster completeness`

### Daily Supply Growth

- `资源副本-角色经验`
  -> `角色升级`
- `资源副本-专武经验`（C-001 目标已确认迁移；当前仅作历史/兼容链观察，是否移除或改造仍待实施）
  -> `专武升级`
- `旅券副本`
  -> `旅券成长`
- `映射装备副本`
  -> `映射装备 / 宝石成长`

### Outer-Loop Growth

- `抽卡`
  -> `box breadth`
- `专武抽卡`（B 裁决：向收容物迁移并保留一个大版本兼容期；实施与工作副本/LIVE 状态待发布证据）
  -> `mechanic depth`
- `商店 / 通行证 / 签到 / 任务`
  -> `resource supplements and growth acceleration`

### Verification Mapping

- `无限挑战`
  checks `long-run endurance and comprehensive account depth`
- `竞技场（PVPVE）`
  checks `competitive efficiency and survivability`
- `爬塔`
  checks `single-team DPS depth`
- `大秘境`
  checks `box breadth, adaptation, and hardcore late-game readiness`
- `BOSS挑战`
  checks `stage-gated boss handling`
