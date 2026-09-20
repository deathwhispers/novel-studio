---
name: write
description: "写指定章节。节拍批量确认 LOOP → 节拍内一次写完 → Critic Lite → 锁定。"
workflow: write-chapter
---

# /novel-studio:write

写指定章节。**节拍批量确认 LOOP + 节拍内一次写完**——写作前一次性确认所有节拍方向，写时只在节拍边界停下，作者把控大方向但不被每段打断。

## 核心原则

- **LOOP 优先**：进入 `/novel-studio:write N` 后第一件事是进入 LOOP 确认本 chunk 所有节拍，**全部锁定 + 选 chunk_mode** 才进入写作
- **节拍内一次写完**：节拍是 200-400 字的微型场景契约，Writer 在节拍内连续写，节拍间按 chunk_mode 决定停/续
- **方向对齐**：LOOP 锁定的 `direction_locked` 是 Writer 不能偏离的指引；segment 模式下 Critic 检查每 beat vs 锁定方向
- **回 LOOP 任意改**：任何阶段都能"回到 LOOP 改 beat-X"，已写节拍也能改（保留旧内容或插入补丁 beat）
- **不硬造钩子**：章尾的悬念和钩子必须从情节自然生长
- **自然分章**：章节按字数（~2000 字）自然收束，写到差不多就找当前情节的自然停顿点结束

## 用法

```
/novel-studio:write <章节号>
/novel-studio:write next
/novel-studio:write

# 可选 flag（写作粒度）
/novel-studio:write <N> --segment        # 每个 beat 停下看（最精细）
/novel-studio:write <N> --super          # 整 chunk 写完，但每章完成后插入 checkpoint
/novel-studio:write <N> --super-strict   # 整 chunk 一气呵成（关闭 checkpoint，原行为）

# 可选 flag（减少干预）
/novel-studio:write <N> --auto           # 自动选默认方向 + chunk_mode super + 自动锁定
```

**flag 优先级**：显式 flag（`--segment` / `--super` / `--super-strict`）直接覆盖默认 `chapter`；无 flag 时阶段 0.45 询问，回车接受 `chapter`。

**`--auto` 模式开关**：

| 行为 | 默认模式 | `--auto` 模式 |
|------|---------|--------------|
| LOOP 阶段 | 展示每个 beat 选项 | 自动选 A，跳过 LOOP |
| chunk_mode 选择 | 询问用户 | 自动 `super`（最快） |
| segment 模式 beat 间停下 | 每 beat 停下 | 不停，连续写完 |
| Critic Lite 软问题 | 用户自决 | 默认通过 |
| 用户锁定确认 | 询问用户 | 自动锁定 |

## 完整流程

### 阶段 0：节拍 LOOP（写作前必走）

#### Orchestrator 入口（断点恢复）

```
📖 当前状态（第 N-1 章结束时）：
   [上一章一句话 + 主角处境 + 活跃伏笔 + 章尾情绪]

检测到你上次停在 chunk-XX 的 [LOOP_PICKING beat-X / WRITING beat-X / REVIEW]。
已确认 Y 个节拍，还有 Z 个未选。

继续？（输入"继续"恢复 / "改"重新选 / "跳过"直接进写作）
```

#### 新 chunk 启动（首次）

```
📖 当前状态（第 N-1 章结束时）：
   [上下文摘要]

本 chunk 主推：
   故事线：[sl-XXX 主题名] — [当前方向]
   人物线：[char-XXX 角色名] — [当前方向]

chunk-XX 还没准备好，我先让 Outliner 设计本 chunk 的节拍（含每节拍选项）。
[N 个 beat，覆盖章节 N-M，当前是第 N 章]

⚠️ 跨卷检测：检查 `outline/volumes/volume-XX.yaml`，若本 chunk 跨卷边界，按 `runtime/state-schema.md` 10.7 拆分——
   - chunk-XX 覆盖 [V1_last_chapter]
   - chunk-XX+1 覆盖 [V2_first_chapter, ...]
   是否需要拆分？（推荐：是 / 强制单 chunk：不推荐）

开始选节拍？
```

**跨卷处理**：用户确认拆分 → Orchestrator 调 Outliner 分别产出两个 chunk 文件；用户坚持单 chunk → 标注"跨卷不拆"风险，进入 LOOP（O6 修复——与 `workflow-specs/write-chapter.md` 0.2 决策树对齐）。
**漂移方向展示**：本 chunk 主推的故事线和人物线由 Outliner 在设计 chunk 时从卷纲/粗大纲提取，Writer 在节拍内严格遵循这两个方向——避免「写着写着忘了大方向」。

#### LOOP_PICKING：逐个确认节拍

```
beat-1：[钩子——承接上章章尾，展示新能力的初次使用]

选项：
  A. 接上章结尾——延续主角在训练场测试的情节
  B. 场景切换——切到测试的旁观者视角
  C. 状态描写——从主角的当前心理切入

你的选择？或：
  - 自定义：[你的方向]
  - D / 你来定：Writer 现场决定（功能不变）
  - 跳到 beat-X：跳到指定 beat
  - 看已选：查看当前 confirmed 摘要
  - 回上一个：回到上一个 beat 重选
  - 全部选完了：即使有 beat 未选也进入 LOOP_PREVIEW
```

#### 阶段 0.45：LOOP_PREVIEW（节拍预览 + chunk_mode 选择）

```
✓ 本 chunk 共 N 个 beat，已确认 X 个（其中 Y 个用"你来定"）。

📊 本 chunk 节奏预览：
  beat-1 [钩子]    → A 接上章结尾       [locked]    ~280 字
  beat-2 [承接]    → B 场景切换        [locked]    ~320 字
  beat-3 [转折]    → C 状态描写        [locked]    ~360 字
  beat-4 [高潮]    → 用户自定义        [custom]    ~400 字
  ...
  预计总字数：~2400 字（±15%）

选择写作粒度（写作中何时停下来让你看）：
  1. segment：每个 beat 写完停下看（最精细）
  2. chapter：每章所有 beat 写完停下看（推荐默认）
  3. super：整 chunk 写完后，**每章完成后插入 super_checkpoint**（chunk 内每章过一次 Lite），chunk 全部完成后整体收口
  4. super-strict：整 chunk 一次性写完 + 一次性 Critic Lite 扫整 chunk——风险高，5 章 × 2K 字 ≈ 10K 远超 Critic 3K 预算，会丢早期信息

[如果估算字数偏差大 → 提示用户回 LOOP 改 beat]

写作粒度（回车 = chapter 推荐档 / --segment / --super / --super-strict）：
> 
```

**super / super-strict 选择指南**（O13 修复，chunk_mode 枚举对齐 `runtime/state-schema.md`）：
- **多数情况选 #3 super**：chunk 内 5 章逐章推进，每章过 Critic Lite（super_checkpoint），最后一章完成后整体收口。**这是默认推荐**
- **少数情况选 #4 super-strict**：用户对整 chunk 方向高度确定、不在乎中间检查、想一口气出稿——但要承担 Lite 质量下降的风险
- **不选 super**：选 segment 或 chapter（最稳健）

**用户响应**：
- 回车 / `chapter` → 默认 chapter 模式（推荐）
- `segment` → 每个 beat 停下
- `super` → 整 chunk 写完但每章完成后插入 checkpoint
- `super-strict` → 整 chunk 一气呵成（关闭 checkpoint）
- `回 LOOP 改 beat-X` → 回到 LOOP_PICKING 重选指定 beat

**为什么先预览再选粒度**：用户对节奏没概念时，被迫在「还没看到全貌」时选粒度容易出错。先看到 7 个 beat 的方向分布，再选「写作中何时停下来」，决策质量更高。

### 阶段 1：节拍驱动写作

#### 写作中（按 chunk_mode）

**章节文件落盘时机**：Writer **每个 beat 写完立即追加**到 `chapters/第N章-XXX.md`（纯正文，无节拍标题，节拍间无视觉分隔）。所有 chunk_mode 通用，作者可随时打开该文件看实时进度。修订已写 beat 时 Orchestrator 告知该 beat 的字符范围，Writer 替换该范围（不重写整章）。用户最后说"锁定"才触发章节事务（StateManager 更新统计字段、汇总 state_delta）。

**segment 模式**：

```
✍️ 第 N 章 · beat-1 写完（已落盘 chapters/第N章-XXX.md）：

[200-400 字正文]

---
这段怎么样？哪里需要调整？
「继续」写 beat-2 / 「改这段」/ 「回 LOOP 改 beat-X」/ 「这章到此结束」
```

> segment 模式：每个 beat 写完立即追加到章节文件。作者在 `chapters/第N章-XXX.md` 看到的就是已完成的章节进度。
>
> segment 模式下每 beat 都过 Critic Lite（含方向一致性检查）——严格保证故事线/人物线方向不漂移。

**chapter/super 模式**（Writer 自动连续写）：

```
✍️ 第 N 章 beat-3 写完（已落盘 chapters/第N章-XXX.md）

[整章进度，至 beat-3 为止]

---
📂 当前已写入 chapters/第N章-XXX.md（持续追加）
继续写 beat-4…/「停一下」/「这章到此结束」
```

> chapter/super 模式：每个 beat 写完立即追加，作者可随时打开章节文件查看当前已完成的全部正文。用户说"这章到此结束"或"锁定" → 进入 Critic Lite + 章节事务。

#### super 模式章节 checkpoint（阶段 1.6，仅 super 模式）

**触发条件**：`chunk_mode == "super"` AND `current.chapter != chapter_range[1]`（非最后一章）。

**最后一章不触发 checkpoint**，直接进入完整 Critic Lite → LOCKED 流程。

```
✅ 第 N 章完成（约 XXXX 字，super 模式 checkpoint）

[Critic Lite 报告——chapter 级检查]

本章结束。下一步：
  1. 继续 super — 写下一章（chapter-N+1），写完继续 checkpoint
  2. 降级为 chapter — 后续章节在阶段 2（每章 Critic Lite）正常停下
  3. 暂停 — 进入 REVIEW，本 chunk 状态保留

你的选择？
```

**用户响应**：
- 继续 super → 重置 current_beat 为下一章 beat-1，继续循环
- 降级 → Orchestrator 把 `chunk_mode` 从 `super` 改为 `chapter`，从下一章开始走普通流程
- 暂停 → `loop_state: "REVIEW"`，等待用户进一步指令

**降级时的状态字段保留**（避免覆盖式重写丢失已写内容）：
- `chunk_plan.beats_written`：保留已写章节的累计值（不重置为 0）
- `chunk_plan.words_written`：保留已写章节的累计字数
- `chunk_plan.confirmed_beats`：保留所有已锁定的 beat（含已写的）
- 用户手改的章节文件：保留不动（Orchestrator 不覆盖）

**为什么需要 checkpoint**：原 super 模式是「整 chunk（5 章）写完才让用户看」，跑偏要等 35+ beat 后才暴露。引入 checkpoint 后每章完成都停下，让用户确认「方向没偏」再继续写下一章。

### 阶段 2：Critic Lite（收尾）

```
✅ 第 N 章初稿完成（约 XXXX 字）

Critic Lite 检查（mode: chapter）：
   - 因果连续性：[通过 / 有几处断裂]
   - 人物一致性：[通过 / 有几处跳变]
   - 文风与排版：[通过 / 有几处 AI 味或排版问题]
   - 方向偏离：[检查每 beat vs direction_locked]
   - 故事线漂移：[检查实际内容 vs active_storyline.direction]
   - 人物线漂移：[检查 POV 角色行为 vs active_character_lines[].direction]

[硬伤回 Writer 修；软问题列给用户]

需要我调整上面这些吗？还是直接锁定？
```

**漂移检查示例**：Critic 报告会包含：

```
   故事线漂移：轻微
     - beat-3：锁定方向"主角发现系统第一秘密"，但实际写成"主角训练新能力"
       （仍推进 sl-002 主角逆袭线，偏离了 chunk 主推的 sl-001）
   人物线漂移：无
     - 主角行为符合"被动接受 → 开始质疑系统"的人物线方向
```

### 阶段 3：用户锁定 + 状态更新

```
📋 正在更新状态…

Writer 汇总本章变更：
- 角色状态变化：[列出]
- 触碰的伏笔：[列出]
- 新埋的伏笔：[列出]
- 读者新获知的信息：[列出]

StateManager 写入（章节事务）：
✅ progress.yaml — total_words +XXXX, total_chapters_written +1, current.chapter +1
✅ chunk_plan.beats_written = 7（本章总数）
（confirmed_beats 不动）

✅ 第 N 章已锁定。
```

### 阶段 4：chunk 收尾（仅最后一章完成后）

```
🎉 chunk-01 全部完成！

StateManager 收尾事务：
✅ outline/chunks/chunk-01.yaml 指针化进 archive
✅ progress.yaml chunk_plan 块清空
✅ transaction-log: trigger=chunk_close

🎯 现在可以：
   1. /novel-studio:write 16 — 继续下一 chunk（Outliner 会基于大纲设计新 chunk）
   2. /novel-studio:outline 调整 — 修改下一 chunk 的某些节拍
   3. /novel-studio:check 11-15 — 对刚完成的 chunk 做体检
```

## 中途调整方向

```
→ 等等，beat-3 的方向不太对。我想换。

✅ 回到 LOOP 改 beat-3。

[重新展示 beat-3 的选项]
```

或：

```
→ 我不喜欢当前的章节大方向，重新选所有节拍。

✅ 回到 LOOP，全部重选。

[清空未写节拍的 confirmed_beats，重新进入 LOOP_PICKING]
```

## 关于手改保留（A6 修复）

> O2 修复后，每个 beat 写完立即追加到章节文件。**作者手改章节文件后**，如果继续写作或重写某个 beat，Writer 会**覆盖作者手改的部分**——这是预期行为，不是 bug。
>
> 若你希望保留手改，请走以下路径：

| 场景 | 推荐路径 |
|------|---------|
| 想手动修订部分段落，保留你的改动 | 用 `/novel-studio:revise <N>`——修订场景专用，Writer 在受限范围内改且不会覆盖你的手改 |
| 想锁定章节不再触发重写 | 用户锁定章节后（"这章到此结束 / 锁定"），Writer 不再重写该章节；后续若需修订，走 `/novel-studio:revise` |
| 想撤回某个 beat 重写 | 用"回 LOOP 改 beat-X"——Orchestrator 告知该 beat 在章节文件中的字符范围，Writer 替换该范围（不重写整章） |
| 章节已锁定但想大改 | `/novel-studio:revise <N>`，StateManager 触发修订事务，保留 `loop_revert_log` 审计 |

**关键点**：不要在被 Writer 写的 beat 区间手动编辑后又触发 Writer 重写——你的手改会被覆盖。如需手改，先触发 `/novel-studio:revise`。

## 快速通道

如果你对整个章节走向非常确定，可以一句话完成 LOOP + 粒度选择：

| 一句话 | 效果 |
|--------|------|
| 「全部按 A 选」 | 跳 LOOP_PICKING，所有 beat 自动选 A |
| 「全部选 A，chunk_mode chapter」 | 跳 LOOP_PICKING（全部 A） + 默认 chapter 粒度 |
| 「全部选 A，--super」 | 跳 LOOP_PICKING（全部 A） + 强制 super（启用 checkpoint） |
| `/novel-studio:write <N> --auto` | 全自动：跳 LOOP（全部 A）+ chunk_mode super + 自动锁定 + 软问题默认通过 |

**`--auto` 的设计目的**：当用户对故事已经胸有成竹、希望"AI 自己写、自动往前推进"时使用——把整套流程的"询问点"压缩到最少，用户只看最后结果，必要时再回 LOOP 调整。

## `--auto` 模式完整示例

以 `/novel-studio:write 11 --auto`（V2 起始章，进入 chunk-13）为例：

```
📖 当前状态（第 10 章结束时）：
   主角刚突破第一瓶颈，情绪觉醒，准备进入下一卷主线。

检测到 V2 起始 + 卷纲缺失——自动让 Outliner 生成 volume-02.yaml...
   ✅ volume-02.yaml 已生成（含 storyline_progress + character_line_progress + phase_map）
   ✅ outline_state.volume_outlines[volume-02].status = "generated"

检测到新 chunk 起始——自动让 Outliner 生成 chunk-13.yaml...
   ✅ chunk-13.yaml 已生成（含 active_storyline + active_character_lines + 7 个 beats）

本 chunk 主推：
   故事线：[sl-001 系统真相线] — 主角初步怀疑系统 → 主角发现第一关键秘密
   人物线：[char-001 主角] — 被动接受系统 → 开始主动质疑系统

--auto 模式：自动选默认方向 + chunk_mode super + 自动锁定
   ✅ 7 个 beat 全部锁定（默认选 A）
   ✅ chunk_mode = "super"
   ✅ Writer 开始写...

✍️ 第 11 章全部 beat 写完（约 2200 字）

📂 已写入 chapters/第011章-觉醒.md

Critic Lite（chapter 级 + 漂移检测）：
   - 因果连续性：通过
   - 人物一致性：通过
   - 文风与排版：AI 味 2 处（轻微）
   - 故事线漂移：无（sl-001 推进正确）
   - 人物线漂移：无（主角表现符合"开始质疑"方向）
✅ 通过（软问题默认通过）

🔒 第 11 章已自动锁定（无硬伤）

[--auto 模式下不询问用户，直接推进]

📂 继续写第 12 章...
[重复相同流程，直到 chunk-13 最后一章]

🎉 chunk-13 全部完成！（V2 起始 5 章）

StateManager 收尾：
   ✅ chunk-13.yaml 归档
   ✅ chunk_plan 清空（含 chunk_mode）
   ✅ outline_state.chunk_designs[chunk-13].status = "archived"

📊 本次运行总结（5 章，约 11000 字）：
   - 推进故事线：sl-001 系统真相线（30%）
   - 推进人物线：char-001 主角（从"被动"到"开始质疑"，30% 进度）
   - AI 味总数：9 处（平均 1.8 处/章，全部为软问题）
   - 漂移事件：0
```

**回退机制**：用户在 `--auto` 模式运行中任何时刻说「暂停 auto」或「手动接管」→ Orchestrator 把 `auto_mode` 设为 false，从下一节点开始恢复正常模式（LOOP_PICKING 重新询问 + Critic Lite 软问题转用户自决）。

**典型使用场景**：
- 用户已经做了几卷，知道 AI 的写作风格——直接 `--auto` 跑一晚
- 用户先在 segment 模式下写了几章调好风格——后续批量 `--auto` 加速
- 用户对 chunk 设计很满意、不想每章确认——`--auto` 减少干扰

## 反模式

见 `workflow-specs/write-chapter.md` 的反模式段。