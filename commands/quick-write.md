---
name: quick-write
description: "用户临时接管某个 beat 自己写，写后纳入正式章节流程。可以跳过 Writer 直接落字。"
---

# /novel-studio:quick-write

**用户临时接管写作**——在节拍 LOOP 流程中，用户可以临时接管某个 beat 自己写，写完后纳入正式章节流程。

## 设计目的

节拍 LOOP 模式下，Writer 通常是 AI。但有些场景用户希望自己写：
- **关键场景**：AI 写得不够到位，用户想亲自操刀
- **灵感爆发**：用户突然有完整段落想直接落字
- **校准风格**：用户先写一段示范风格，让 AI 学习后续章节
- **修订后落盘**：用户在 revise 后想直接写补丁段落

`/novel-studio:quick-write` 提供绕过 Writer 的通道，但保持与 LOOP 的衔接（确认/锁定/Critic Lite 照常进行）。

## 用法

```
/novel-studio:quick-write <章节号> <beat-id>   # 在指定章节的指定 beat 接管写作
/novel-studio:quick-write <章节号>             # 在指定章节的当前 beat 接管写作
/novel-studio:quick-write append <章节号>        # 在指定章节末尾追加段落（不绑定 beat）
```

## 适用场景

| 场景 | 用法 |
|------|------|
| 关键对话场景 | `/novel-studio:quick-write 11 beat-3` → 接管 beat-3 |
| 灵感爆发的补丁 | `/novel-studio:quick-write 12 append` → 在第 12 章末尾追加一段 |
| 校准风格 | `/novel-studio:quick-write 10 beat-1` → 写 beat-1，让 AI 模仿后续 |

## 不适用场景

- **新增新 beat**：quick-write 不创建 beat，只接管已有 beat
- **跨章节接管**：quick-write 不支持跨章节接管，每次操作限于单章节
- **覆盖已落盘章节**：quick-write 不会覆盖完整章节文件，只能在 beat 槽位写入或 append

## 对话流程

### 阶段 0：Orchestrator 入口

```
📖 当前状态（第 N-1 章结束时）：
   [上下文摘要]

检测到第 N 章处于 WRITING 状态（beat-X 已锁未写）
  或 LOOP_PICKING 状态（全部 beat 已锁，chunk_mode 已选）
  或 REVIEW 状态（已写完进入等用户指令）

quick-write 接管目标：beat-X（或 append）

继续？（输入"继续"接管 / "选 beat"指定 / "取消"回到正常流程）
```

### 阶段 1：用户接管写作

用户直接写出 beat 文本：

```
> 「主角推开仓库门，铰链声在夜里格外刺耳。

他没说话。仓库深处的呼吸声比铰链声更让他警觉。

'出来。'

月光从屋顶的破洞漏下来，照亮了角落里的血迹。」

[用户继续写...]
```

**Orchestrator 行为**：
- 接收用户文本
- **不调用 Writer**——本 beat 由用户完成
- 标记 `confirmed_beats[beat-X].source: "user_quick_write"` + `quick_write_at: <now>`（新增第五种 source，与 schema 第十二节保持一致）
- **★ 在 `chunk_plan.quick_write_log[]` 追加条目**（数据模型唯一真值）：

```yaml
chunk_plan:
  quick_write_log:
    - beat_id: "beat-3"
      mode: "beat_replace"          # beat_replace | append
      chapter: 11
      word_count: 320
      written_at: "<now>"
      # 完整文本存在章节文件中；log 只存指针 + 元数据，避免 progress.yaml 膨胀
      chapter_offset: { start: 1245, end: 1565 }   # Orchestrator 写入时记录字符范围
```

**为什么用 `quick_write_log` 而非 `confirmed_beats[].quick_write_output`**：
- 完整文本存章节文件（O2 修复后已落盘），`progress.yaml` 不应该再复制一份
- `confirmed_beats[].source: "user_quick_write"` 已足够标识这是用户接管的 beat
- `quick_write_log` 是元数据审计轨迹（哪个 beat 在什么时候被用户接管了）——方便后续断点恢复时识别

### 阶段 2：字数控与边界检查

```
✅ beat-X 已接管（约 XXX 字）

字数检查：target_words=350 ±15%（296-404 字）
  - 你的版本：XXX 字 ✓ 符合

boundary 检查：是否写到 next_beat_starter 描述的内容？
  - 你的版本停在：「月光从屋顶的破洞漏下来」
  - next_beat_starter：「主角发现地上的尸体」
  - ✓ 未越界

下一步：
  1. 接受 → 标记为完成，进入下一 beat 或下一章
  2. 调整 → 继续编辑
  3. 取消 → 放弃本次接管，回到上一 beat 状态
```

### 阶段 3：进入下一阶段（与正常流程相同）

按 beat_mode / chunk_mode 继续：
- segment 模式：进入下一 beat（如果还有）或 Critic Lite
- chapter/super 模式：进入下一 beat（Writer 自动接管）
- LOOP_PICKING 模式：回到 LOOP（用户可改本 beat 方向）

### `append` 模式特殊处理

```
/novel-studio:quick-write 12 append
```

```
📖 当前状态：第 12 章已写完（Review 状态）

append 模式：在章节末尾追加段落

[用户写：]
> 「第二天，主角醒来，发现枕边多了一封信。」

✅ append 已完成（+XX 字）

当前第 12 章：约 2300 字（原 2200 字 + append 200 字）

**Orchestrator 落盘 + 状态**：
- 章节文件追加用户文本（O2 修复后 Writer 自追加）
- `chunk_plan.quick_write_log[]` 追加：

```yaml
chunk_plan:
  quick_write_log:
    - beat_id: null                  # append 模式无 beat 绑定
      mode: "append"
      chapter: 12
      word_count: 200
      written_at: "<now>"
      chapter_offset: { start: 2245, end: 2445 }
```

下一步：
  1. 接受 → 更新 chapter_word_target 估算，进入 Critic Lite
  2. 调整 → 继续追加或编辑
  3. 取消 → 放弃本次 append，章节字数不变
```

**append 的用途**：
- **补丁型补充**：在已锁章节后补一段（如 "上一章太短，补充一个场景"）
- **过渡型衔接**：为下一章铺垫
- **不重写整章**：append 只在末尾追加，不覆盖已有内容

## 与正常 LOOP 的区别

| 维度 | 正常 LOOP | quick-write |
|------|---------|-------------|
| 调用方 | Writer（AI） | 用户 |
| 文本来源 | WriterBrief-Beat | 用户直接输入 |
| 字数控制 | Writer 自检 + Critic Lite 兜底 | Orchestrator 即时检查 + 用户确认 |
| 边界检查 | Writer 自检 + Critic Lite | Orchestrator 即时检查 |
| beat 归属 | `source: "option"/"custom"/"ai_improvised"` | `source: "user_quick_write"` |
| 状态机 | 正常推进 | 同上（用同一条 `current_beat` 推进） |
| 断点恢复 | 正常恢复 | 正常恢复（quick_write_output 已存盘） |

## 落盘与状态字段

quick-write 完成后：
- `confirmed_beats[beat-X].source: "user_quick_write"`（与 schema 第十二节 source 枚举一致——已扩展为第五种来源，详见 `runtime/state-schema.md`）
- `chunk_plan.quick_write_log[]` 追加本次记录（含 `mode: beat_replace | append` + `word_count` + `written_at` + `chapter_offset`）
- 章节文件：纯正文直接落盘（O2 修复后已自动落盘）；append 模式用 Writer 的章节文件追加协议
- 状态文件：StateManager 章节事务照常更新（用户接管的内容也算 `beats_written += 1`）

## 反模式（禁止）

- ❌ 用 quick-write 替代 Writer 写完全章节（应让 Writer 在节拍 LOOP 框架下发挥）
- ❌ 在 quick-write 中改大纲方向（方向锁定由 LOOP_PICKING 决定，quick-write 只接管文本不接管方向）
- ❌ 用 quick-write 跳过节拍 LOOP 的流程纪律（如跳过 Critic Lite）
- ❌ 把 quick-write 当作"我比 AI 写得好"的工具——quick-write 是协作工具，不是替换

## 典型使用场景示例

### 示例 1：关键对话场景

```
/novel-studio:write 11 --auto
  → 自动 LOOP（全部 A）+ super + auto_mode=true
  → Writer 写 beat-1, beat-2...
  → beat-3（关键对话：主角与反派首次摊牌）

✍️ beat-3 写完（AI 版）

→ 等一下，这段对话不对。我想亲自写。

/novel-studio:quick-write 11 beat-3

> 「主角：'你以为你在操纵我？'
  反派：'不是操纵，是筛选。'
  主角沉默了三秒，然后笑出声来。
  '那你现在选错了人。'」

✅ beat-3 quick-write 完成（替换 AI 版）
✅ 后续 beat-4~7 由 Writer 继续（auto 模式）
✅ Critic Lite 报告：beat-3 通过（用户接管）
```

### 示例 2：append 补丁

```
/novel-studio:check 12
  → 报告：第 12 章结尾太突兀

/novel-studio:revise 12
  → 选择"局部修复"→ Writer 修了一些对话
  → 你觉得还不够

/novel-studio:quick-write 12 append
> 「主角推开门，夜色比来时更深。他没有回头。」

✅ append 完成
✅ 第 12 章从 2200 字 → 2280 字
✅ 进入 Critic Lite 检查（包括 append 部分）
```

## 核心原则

- **quick-write 是协作工具**：用户接管某个 beat，与 Writer 协作完成章节，不是"AI 不能写"
- **保持流程纪律**：quick-write 仍受方向锁定约束、字数控制、边界检查、Critic Lite 兜底
- **用户接管不绕开 Critic**：quick-write 的文本也要过 Critic Lite（虽然不像 AI 写得那么需要，但仍需检查是否触碰 forbid_touch 等）
- **落盘语义一致**：quick-write_output 跟 Writer 输出走同一套 WriterBrief-Beat → chapter 文件落盘逻辑
- **断点恢复兼容**：quick-write 后的 beat 也支持断点恢复（已存 confirmed_beats[beat-X].quick_write_output）