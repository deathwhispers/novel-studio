---
name: storyline-drift-check
description: "故事线漂移检测。检查写作产出是否推进了 chunk.active_storyline.direction（剧情主题方向）。纯能力，由 Critic Lite 4 调用。"
category: analysis
---

# 故事线漂移检测

> 检查当前写作内容是否仍属于 chunk 设计主推的故事线方向——避免「写着写着跑偏到其他剧情主题」。

## 何时调用

Critic Lite 在写章节收尾时调用（仅当 `chunk_mode` 触发 Critic Lite）：
- `mode: segment` — 每个 beat 写完后
- `mode: chapter` — 整章写完后
- `mode: super` — 每个 super_checkpoint（mid-chunk 暂停点）或整 chunk 完成后

## 数据来源

`CriticBrief-Lite.drift_check.storyline_expected`：
- `storyline_id`: 当前 chunk 主推的故事线 ID
- `direction`: 当前故事线的方向描述（如「主角初步怀疑系统 → 主角发现系统的第一关键秘密」）
- `carrier`: 这条线本段主要由谁推进（如「主角」）

## 检测流程

### 步骤 1：实际推进检查

对照 `storyline_expected.direction`，扫描写作产出：

- [ ] **方向起点对齐**：实际内容是否从 `direction` 的起点开始？（如果 chunk 设计期望「主角初步怀疑系统」，实际内容是否在表现主角开始质疑？）
- [ ] **方向终点靠近**：实际内容是否在向 `direction` 描述的终点靠近？（如实际是否在接近「发现第一关键秘密」？）
- [ ] **核心事件对应**：`direction` 中描述的关键事件是否发生？或部分发生？

### 步骤 2：推进者检查

- [ ] `carrier`（推进者）是否参与了实际推进？
- [ ] `carrier` 是否在场？（如果 carrier 是主角，主角是否出现在本 beat/chapter 中？）
- [ ] `carrier` 的相关动作/思考/对话是否体现推进？

### 步骤 3：主线漂移检查（关键）

- [ ] 实际写出的内容是否属于其他 storylines（如 chunk 主推 sl-001 但实际写了 sl-002 的内容）？
- [ ] 这种跨线写作是否合理（如有交叉点设计且当前确实是交叉章节）？

## 输出格式

```yaml
storyline_drift_report:
  drift_severity: "无/轻微/严重"     # 严重度判断见下表
  issues:
    - beat_id: "beat-3"
      location: "..."
      severity: "轻微"
      type: "主线漂移"             # 主线漂移 | 推进者缺失 | 终点偏离
      description: "chunk 主推 sl-001 '系统真相线'，但实际写成 sl-002 '主角逆袭线' 的内容"
      fix: "将 beat-3 内容调整回 sl-001 方向，或回 LOOP 改 beat-3 的 direction_locked"
    - beat_id: "beat-2"
      severity: "严重"
      type: "推进者缺失"
      description: "carrier 是 '主角'，但 beat-2 主角完全未出场，副角主导了剧情"
      fix: "补充主角视角或调整 carrier（需回 LOOP）"
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

1. **不修改正文，只标注问题** — 修复由 Writer 执行
2. **跨线写作不一定是错** — 检查是否在 storylines_crossings 设计的交叉点
3. **主线漂移优先于推进者缺失** — 主线偏离是结构性问题，必须修
4. **轻微偏离允许** — 单次 beat 的小偏离不构成硬伤，多 beat 累积才是
5. **与人物线漂移互补** — 故事线是"剧情主题"维度，人物线是"角色成长"维度，可独立漂移