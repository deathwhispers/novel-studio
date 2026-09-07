# Scene Card 模板（用于系统文）

目的：为每个场景提供固定节拍与可验证输出，保证写作在不改变主体情节下有机增强。

字段说明：
- id: 场景唯一标识
- chapter: 所属章节编号或标题
- hook: 一句 1-2 行的强钩子（引发读者好奇）
- system_task: |
  - task_id: 系统任务标识
  - description: 任务简述（含时限/奖励）
  - trigger_condition: 触发条件或前置事件
- expected_conflict: 本场景主要阻碍与来源（对手/环境/内心）
- sensory_notes: 至少 2 处感官细节提示
- panel_effects: 若任务完成或失败，面板变化声明（或 `none`）
- reader_emotion: 预期读者情绪（例：好奇/愤怒/同情）
- end_hook: 章节结尾钩子（用于推进下一场景）

生成指令示例（给 Writer）：
"按上面字段输出场景文本，保持主线不变；若需要更改系统面板，请在 `panel_effects` 返回 `panel_patch`（字段、old->new、原因）。文本需要包含 2 处以上感官描写，并在段落末尾标注对应的 scene-card 字段引用。"
