---
name: character-line-drift-check
description: "人物线漂移检测。检查 POV 角色的行为是否符合 chunk.active_character_lines[].direction（角色成长方向）。纯能力，由 Critic Lite 5 调用。"
category: analysis
---

# 人物线漂移检测

> 检查 POV 角色的行为是否仍符合人物线方向——避免「角色突然不像自己」或「成长方向与设计背离」。

## 何时调用

Critic Lite 在写章节收尾时调用（仅当 `chunk_mode` 触发 Critic Lite）：
- `mode: segment` — 每个 beat 写完后
- `mode: chapter` — 整章写完后
- `mode: super` — 每个 super_checkpoint（mid-chunk 暂停点）或整 chunk 完成后

## 数据来源

`CriticBrief-Lite.drift_check.character_line_expected`：
- `character_id`: 当前 chunk 主推的人物线对应的 POV角色 ID
- `direction`: 当前人物线的成长方向（如「被动接受系统 → 开始主动质疑系统」）
- `growth_target`: 本 chunk 末角色应完成的成长目标（如「第一次违抗系统指令」）

## 检测流程

### 步骤 1：成长方向检查

对照 `character_line_expected.direction`，扫描写作产出：

- [ ] **起点对齐**：实际内容是否从 `direction` 的起点状态开始？（如人物线起点是「被动接受系统」，主角是否表现出被动接受？）
- [ ] **成长推进**：实际内容是否推进角色向 `direction` 描述的终点变化？（如人物线终点是「开始主动质疑系统」，主角是否在逐步质疑？）
- [ ] **成长目标达成**：`growth_target`（如有）是否完成？（如「本 chunk 末主角应完成：第一次违抗系统指令」，是否真的违抗了？）

### 步骤 2：角色一致性检查（与 Character Lite 互补）

- [ ] 角色的行为是否可以从其 want/fear/wound 理解？
- [ ] 角色是否有「突然像另一个人」的时刻？（如一直谨慎的主角突然冒险，违反人设）
- [ ] 对话/动作是否符合角色的 `surface.speech_pattern` + `mannerisms`？

### 步骤 3：跨人物线漂移检查

- [ ] POV 角色是否突然展现出属于其他角色的弧光方向？（如主角弧光是「被动→主动质疑」，但行为更符合反派的弧光「目的驱动→动摇」）
- [ ] 这种漂移是否合理（如有 crossing 设计且当前是交叉点）？

## 输出格式

```yaml
character_line_drift_report:
  drift_severity: "无/轻微/严重"
  issues:
    - beat_id: "beat-2"
      location: "..."
      severity: "轻微"
      type: "成长方向偏离"
      description: "POV 主角人物线方向是 '被动接受系统 → 开始主动质疑系统'，但 beat 中主角仍完全顺从系统指令，没有任何质疑表现"
      fix: "在 beat-2 加入主角的内心犹豫或外在质疑行为"
    - beat_id: "beat-3"
      severity: "严重"
      type: "角色行为不一致"
      description: "一向谨慎的主角突然主动暴露能力，违反其 'want: 隐藏实力' 的设定"
      fix: "补充主角暴露能力的动机铺垫（如系统限时只剩30秒），或改为被动暴露"
```

## 漂移严重度判断（按 mode 分档）

| 严重度 | segment | chapter | super |
|----------|---------|---------|-------|
| 无 | 0 beat 偏离 | 0 处偏离 | 0 处偏离 |
| 轻微 | 1 beat 偏离 | 1-2 处偏离 | 1-3 处偏离 |
| 严重 | ≥2 beat 偏离 | ≥3 处偏离 | ≥4 处偏离 |

## 失败处理（与 Lite 判决联动）

| 严重度 | 判决 | 后续动作 |
|--------|------|---------|
| 无 | 通过 | 进入用户锁定 |
| 轻微 | 用户自决 | 列给用户决定修或不修 |
| 严重 | 就地修 | 回 Writer 限定范围修改 |

## 核心原则

1. **人物线 ≠ 故事线** — 故事线是"剧情主题"（如系统真相），人物线是"角色成长"（如主角从被动变主动）
2. **不修改正文，只标注问题** — 修复由 Writer 执行
3. **成长是渐进的** — 主角不会突然从起点跳到终点，每章推进一点点即可
4. **角色一致性优先** — "成长方向偏离"是软问题，"角色突然像另一个人"是硬伤
5. **人物线失败处理与 Character Lite 互补** — Character Lite 查全章行为一致性，人物线 Lite 查成长方向一致性
6. **与故事线漂移互补** — 一个角色可以同时推进多条故事线，单条故事线漂移不等于人物线漂移