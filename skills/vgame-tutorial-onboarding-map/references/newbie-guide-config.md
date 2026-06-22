# Newbie Guide Config (Out-of-Battle)

## 编辑工具

Unity 编辑器窗口: `GuideEditorWindow.cs`
- 菜单入口: Unity Editor 内
- 持久化: `GuideEditorData.json`
- 导出: → `GuideSequenceData_Auto.lua` + `GuideStepData_Auto.lua`

## Sequence（引导序列）

一个 Sequence 是一组连续引导步骤的集合，描述"引导玩家完成一个功能的首次使用"。

| 字段 | 类型 | 说明 |
|---|---|---|
| Id | int | 序列唯一ID |
| Name | string | 人类可读名称 |
| SortOrder | int | 优先级排序 |
| StartType | int | 1=强制打开UI, 2=等待UI自然打开 |
| StartUI | string | 目标UI面板名 |
| SubTargetUI | string | 动态子UI名 |
| StartUIOpenParams | table | 强制打开时的参数 |
| SequenceDelayTime | int(ms) | 强制打开前延迟 |
| FailureLevel | int | 0=永不失败, 1=静默跳过, 2=跳步, 3=跳序列 |
| UnlockId | int | 触发条件（关联Unlock表，必须已解锁） |
| ExpireId | int | 过期条件（已解锁则不再触发） |
| NextSequence | int | 完成后链接的下一个序列ID |
| NextStep | int | 下一序列从哪步开始 |
| AllowSkip | bool | 玩家能否跳过 |
| IsValid | bool | 是否启用 |

## Step（引导步骤）

一个 Step 是序列中的单个操作指引。

| 字段 | 类型 | 说明 |
|---|---|---|
| Id | int | 步骤ID |
| SequenceId | int | 所属序列 |
| StepOrder | int | 序列内排序 |
| StepType | int | 1=点击目标, 2=点击任意处, 3=定时关闭, 4=拖拽 |
| TargetUI | string | 目标UI面板 |
| TargetNode | string | 目标节点Key（ObjectBinder绑定的guide node） |
| SubTargetUI | string | 动态子UI |
| SubTargetUIIndex | int | 子UI实例索引 |
| TargetItemIndex | int | 列表项索引（动态列表中的第N个） |
| StepValue | string | 定时ms(Type=3) 或 拖拽目标节点(Type=4) |
| MaskType | int | 0=无, 1=圆形高亮, 2=矩形高亮, 3=全屏透明 |
| MaskOffset | vector | 遮罩偏移 |
| MaskSize | vector | 遮罩尺寸 |
| ErrorOperationTip | string | 点错位置时的提示文字 |
| GuideBubble | string | 气泡图片资源 |
| GuideText | string | 气泡内文字 |
| GuideArrow | string | 箭头图片资源 |
| FingerType | int | 手指动画类型 |
| GuideSound | string | 音效 |
| DelayBefore | int(ms) | 执行前延迟 |
| AllowPassThrough | bool | 点击任意处时也触发底层UI |
| IsSequenceEndNode | bool | 此步完成时上报服务器 |

## 执行流程

```
NewbieGuideSystem.OnInit()
  → 加载配置(SequenceData + StepData)
  → 监听 ConditionEvent.OnSystemUnlock / OnLevelUnlock
  → 恢复服务器进度

收到解锁事件:
  → _CheckAndEnqueueSequences()
    → 遍历所有 Sequence
      → Check UnlockId 已满足
      → Check ExpireId 未满足
      → Check IsValid = true
      → 入队 _guideQueue

TryStartNextSequence():
  → 出队
  → StartSequence(seqId):
    if StartType == 1 (ForceJumpUI):
      → 强制打开目标UI面板
      → 等待面板打开完成
      → _DoStartSequence()
    if StartType == 2 (WaitUIOpen):
      → 检查目标面板是否已打开
      → 是 → _DoStartSequence()
      → 否 → 监听面板打开事件

_DoStartSequence():
  → RunStep(第1步)

RunStep(stepIndex):
  → 获取 StepData
  → 检查 TargetUI 是否打开（未打开则等待）
  → DelayBefore 延迟
  → _ShowGuideUI():
    → 打开 UIGuideView
    → 设置遮罩(MaskType + Offset + Size)
    → 设置气泡(GuideBubble + GuideText)
    → 设置箭头(GuideArrow)
    → 设置手指动画(FingerType)
  → _SetupStepCompletionDetection():
    if StepType == 1 (ClickTarget):
      → 在 TargetNode 上挂 GuideTargetRelay
      → 监听点击事件
    if StepType == 2 (ClickAnywhere):
      → 全屏点击即完成
    if StepType == 3 (Timer):
      → StepValue ms 后自动完成
    if StepType == 4 (Drag):
      → 在 TargetNode 上挂 GuideDragRelay
      → 验证拖拽到 StepValue 指定目标

CompleteStep():
  → 清理UI
  → if IsSequenceEndNode: 上报服务器
  → NextStep() 或 EndSequence()

EndSequence():
  → 标记完成
  → 同步服务器
  → if NextSequence: 启动链接序列
  → TryStartNextSequence() (处理队列中下一个)
```

## 失败处理 (FailureLevel)

| 级别 | 行为 |
|---|---|
| 0 (永不失败) | 一直重试直到成功 |
| 1 (静默跳过) | 目标找不到时静默跳过该步 |
| 2 (跳步) | 该步失败后跳到下一步 |
| 3 (跳序列) | 该步失败后整个序列标记完成 |

## 服务器同步

- 已完成序列列表同步到服务器（`PlayerClientInfo`）
- 断线重连后从服务器恢复进度
- `IsSequenceEndNode` 控制哪些节点上报（不是每步都上报）

## 设计注意事项

| 注意 | 说明 |
|---|---|
| TargetNode 必须存在 | UI 面板中必须有 ObjectBinder 绑定对应 key 的节点 |
| SubTargetUI 时序 | 动态加载的子UI可能有延迟，需要配合 DelayBefore |
| 列表项引导 | TargetItemIndex 要确保列表已加载到该索引 |
| 强制打开冲突 | ForceJumpUI 时如果有其他弹窗挡住可能失败 |
| ExpireId 设置 | 避免玩家已经自己学会了功能后还被强制引导 |
| AllowSkip | 非核心引导建议允许跳过，避免打扰老玩家 |
