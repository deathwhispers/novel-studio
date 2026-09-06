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
```

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

chunk-01 还没准备好，我先让 Outliner 设计本 chunk 的节拍（含每节拍选项）。
[N 个 beat，覆盖章节 11-15，当前是第 11 章]

开始选节拍？
```

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
  - 跳到 beat-X：跳到指定节拍
  - 看已选：查看当前 confirmed 摘要
  - 回上一个：回到上一个 beat 重选
  - 全部选完了：即使有 beat 未选也进入写作
```

#### LOOP_DONE：选写作粒度

```
✓ 本 chunk 共 7 个 beat，已确认 X 个（其中 Y 个用"你来定"）。

选择写作粒度（写作中何时停下来让你看）：
  1. segment：每个 beat 写完停下看（最精细）
  2. chapter：每章所有 beat 写完停下看（推荐）
  3. super：整个 chunk 写完才停

你的选择？
```

### 阶段 1：节拍驱动写作

#### 写作中（按 chunk_mode）

**segment 模式**：

```
✍️ 第 N 章 · beat-1 写完：

[200-400 字正文]

---
这段怎么样？哪里需要调整？
「继续」写 beat-2 / 「改这段」/ 「回 LOOP 改 beat-X」/ 「这章到此结束」
```

**chapter/super 模式**（Writer 自动连续写）：

```
✍️ 第 N 章全部 beat 写完（约 XXXX 字）：

[整章正文]

---
看看整章？需要调整吗？
```

#### 用户操作映射

| 用户说 | 动作 |
|--------|------|
| 「继续」/「A」/「下一段」 | `beats_written +1`，调 Writer 写下一个 beat（segment 模式） |
| 「改这段：[问题]」 | Writer 修订当前 beat（限本 beat 范围，不改 confirmed_beats） |
| 「回 LOOP」/「改 beat-X」 | 进入 LOOP 重入，target beat 设为 `locked: false` |
| 「这章到此结束」 | 提前进入 Critic Lite（即使本章 beat 未全写完） |
| 「写下一章」/「next」 | 锁章 → 推进到下一章 → 进入 LOOP（chunk 已存在） |

### 阶段 2：Critic Lite（收尾）

```
✅ 第 N 章初稿完成（约 XXXX 字）

Critic Lite 检查（mode: chapter）：
   - 因果连续性：[通过 / 有几处断裂]
   - 人物一致性：[通过 / 有几处跳变]
   - 文风与排版：[通过 / 有几处 AI 味或排版问题]
   - 方向偏离：[检查每 beat vs direction_locked]

[硬伤回 Writer 修；软问题列给用户]

需要我调整上面这些吗？还是直接锁定？
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

## 快速通道

如果你对整个章节走向非常确定，可以说「全部按 A 选」/ 「全部选 A，chunk_mode chapter」——一句话完成 LOOP + 粒度选择。

## 反模式

见 `workflow-specs/write-chapter.md` 的反模式段。