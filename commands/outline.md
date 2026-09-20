---
name: outline
description: "设计故事大纲。多轮深度对话构建 3 段大纲：粗大纲（必做，含故事线+人物线+分卷）+ 卷纲（按需）+ chunk 设计（按需）。"
workflow: outline
---

# /novel-studio:outline

设计故事大纲。**3 段大纲体系**——粗大纲（必做）+ 卷纲（写到该卷时按需生成）+ 近几章剧情细化（写章节时按需生成）。不预先生成所有大纲，避免一次填完所有细节的负担。

## 核心原则

- **故事线和人物线分离驱动**（核心新原则）：
  - **故事线** = 剧情主题（穿越多个角色），如「系统真相线」「主角逆袭线」
  - **人物线** = POV 角色成长（每个角色独立完整），如「主角：被动→主动质疑」「反派：冷酷→动摇」
  - 两者**不合并**，在卷纲/chunk 设计中显式映射
- **段 1 即可开写**：粗大纲（故事线 + 人物线 + 分卷粗规划）确认后即可开写，卷纲和 chunk 设计在写作时按需补
- **规划到卷，不规划到章**：见 `agents/outliner.md` 核心原则
- **小步快爬**：每段只细化到能开始下一步的程度，不一次性把全书写完大纲
- **每段确认**：每一段设计都和你确认后才进入下一段

## 用法

```
/novel-studio:outline                                    # 创建新大纲（段 1 粗大纲）
/novel-studio:outline 调整                              # 调整已有大纲（故事线/人物线/卷纲/chunk）
/novel-studio:outline 检查                              # 检查大纲（漂移检测 + 健康度扫描）
/novel-studio:outline 迁移                              # 旧 5 层大纲 → 3 段大纲（一次性，谨慎）

# 可选 flag
/novel-studio:outline --auto                            # 自动确认 Outliner 方案 + 跳过可选层
```

## 对话流程

### 入口

```
📐 3 段大纲设计。你想做什么？

1. 创建新大纲（段 1：粗大纲 → 即可开写，段 2/3 按需补）
2. 调整已有大纲（故事线 / 人物线 / 卷纲 / chunk）
3. 检查大纲（漂移检测 + 健康度扫描）

或者直接说你想做什么。
```

---

### 段 1：粗大纲（必做，3 轮对话）

#### 第 1 轮：核心冲突与主题

```
先不聊章节划分——聊故事的内核。

基于你的项目设定 [已有设定的摘要]，我想确认：

1. 这个故事的核心冲突是什么？
   不是「主角打反派」——是更深层的冲突。
   比如：个人意志 vs 命运安排 / 自由 vs 秩序 / 守护 vs 牺牲

2. 如果这个故事只能让读者记住一件事，你希望是什么？

3. 你脑子里有没有一个「绝对要写」的场景或转折？
   不一定在哪一章——就是你一想到这个故事就兴奋的那个画面。
```

等待用户回答。复述理解。

#### 第 2 轮：拆解故事线和人物线（核心新步骤）

```
好的，基于你说的，我来拆两套线——

【故事线】——以"剧情主题"为单位，穿越多个角色：

   故事线 1：[主题名]
     讲的是：[一句话]
     推进者：[谁在这条线上推进]
     赌注：[失败了会怎样]
     收束于：[第 X 卷]

   故事线 2：[主题名]
     ...

【人物线】——以"角色"为单位，每个 POV 角色独立成长：

   主角 [主角名]
     方向：[从什么状态 → 经过什么 → 走向哪里]
     成长方向：[内在从 A → B]

   配角 [配角名]
     方向：[独立完整的起承转合，不依附主角]
     推进哪条故事线：[配角参与哪条故事线的推进]

你觉得这个拆解对吗？
- 加线 / 删线 / 改线？
- 故事线和人物线的对应关系对吗？（是否每条故事线都有角色推进？每个角色都参与故事线吗？）
- 人物线之间有交叉吗？（如主角的弧光影响反派的弧光）
```

用户可以修改、增减故事线和人物线。确认后进入下一轮。

#### 第 3 轮：分卷粗规划

```
有了故事线和人物线，来分卷。

每卷是"所有线共享的时间容器"——

   第一卷（约 X-Y 章）：[卷名]
   ───────────
   功能：[引入/展开/转折/高潮/收束]
   主推故事线：[故事线 ID + 主题名]
   辅推故事线：[故事线 ID + 主题名]
   重点人物线：[角色 ID + 名字]

   第二卷（约 X-Y 章）：[卷名]
   ───────────
   ...

   总计约 Z 卷，约 XXX 章。

确认后即可开写——卷纲会在写到该卷起始章时自动生成（你不需要手动做）。
chunk 设计也会在写到新 chunk 起始章时自动生成。
```

用户调整确认后，进入收尾。

#### 收尾：生成粗大纲文件

```
✅ 粗大纲完成。

生成以下文件：
   outline/全书总纲.yaml    — 故事线 / 人物线 / 分卷粗规划

🎯 现在可以：
   1. /novel-studio:write 1   — 直接开始写（卷纲和 chunk 设计会在写章节时按需补）
   2. /novel-studio:outline 调整 — 微调故事线 / 人物线 / 分卷
```

**注意**：卷纲（段 2）和 chunk 设计（段 3）**不需要**在 `/novel-studio:outline` 命令中生成——它们在写章节时由 Orchestrator 自动调 Outliner 产出。

---

### 段 2：卷纲（按需生成，写作时透明完成）

卷纲不需要用户在 `/novel-studio:outline` 命令中手动生成。**当用户写到某卷起始章时**，Orchestrator 会自动调 Outliner 产出 `outline/volumes/volume-XX.yaml`：

- 输入：粗大纲中的该卷粗规划（function / line_primary / line_secondary / character_focus）
- 输出：完整的卷纲（含 storyline_progress + character_line_progress + phase_map + turning_points + volume_end_hook）
- **对用户透明**：不弹额外对话，自动完成

如果用户希望主动查看/调整某卷的卷纲：

```
/novel-studio:outline 查看卷纲 volume-XX
/novel-studio:outline 调整卷纲 volume-XX
```

调整项：storyline_progress / character_line_progress / phase_map / turning_points / volume_end_hook。

---

### 段 3：chunk 设计（按需生成，写章节时透明完成）

chunk 设计不需要用户在 `/novel-studio:outline` 命令中手动生成。**当用户写到新 chunk 起始章时**，Orchestrator 会自动调 Outliner 产出 `outline/chunks/chunk-XX.yaml`：

- 输入：卷纲 + 粗大纲 + 上一 chunk 尾巴（如有）
- 输出：完整的 chunk 设计（含 beats[] + active_storyline + active_character_lines + 每 beat 的 advancing_storyline / advancing_character_line）
- **对用户透明**：不弹额外对话，自动完成

如果用户希望主动查看/调整某 chunk：

```
/novel-studio:outline 查看 chunk-XX
/novel-studio:outline 调整 chunk-XX
```

调整项：beats[]（添加/删除/修改）+ active_storyline + active_character_lines。

---

### 段 4：伏笔地图（可选参考文件）

伏笔地图是可选的参考文件，**不在 `/novel-studio:outline` 命令中强制生成**。你可以主动维护 `outline/伏笔地图.yaml`，包含伏笔的埋设/轻碰/回收规划：

```yaml
# outline/伏笔地图.yaml
foreshadows:
  - id: "fs-001"
    description: "玉佩发光的秘密"
    plant_volume: 1
    plant_position: "中段"
    plant_detail: "主角获得玉佩时闪过一丝光"
    payoff_volume: 3
    payoff_position: "卷末"
    payoff_detail: "玉佩其实是XX文明的钥匙"
    line: "sl-001"
    status: "planned"
```

伏笔追踪的运行时状态（`active` / `touched` / `resolved` 等）由 StateManager 在 `state/foreshadow.yaml` 中维护——你只需要在大纲阶段规划好埋设和回收点，写作时按需填写。

> 与段 1/2/3 不同：伏笔地图不是必做项，可以等写章节时遇到具体伏笔再补。

---

### 旧 5 层大纲迁移（一次性）

如果你的工作区是 0.1.2 之前创建的（有旧 5 层大纲文件：`outline/故事线交错.yaml`、`outline/角色弧光.yaml`、`outline/伏笔地图.yaml`），可使用 `/novel-studio:outline 迁移` 命令将旧大纲迁移到新 3 段格式。

**迁移流程**：

```
📐 检测到旧 5 层大纲文件：
   - outline/全书总纲.yaml（旧版本，含 storyline.character 单角色绑定）
   - outline/故事线交错.yaml（interweave_map）
   - outline/角色弧光.yaml（character_arcs）
   - outline/伏笔地图.yaml（旧版本，foreshadows[].line 字段）

迁移计划：
   1. 备份：所有旧文件复制到 outline/archive-v1.2/（带时间戳）
   2. 粗大纲改造：
      - storylines[].character → storylines[].key_characters[]（单角色 → 数组）
      - storylines[].stakes + resolution_volume 保留
      - 新增 character_lines[] 板块：从角色档案 + 旧角色弧光生成
   3. 故事线交错 → 合并到粗大纲 storyline_crossings[] + 卷纲 turning_points[].affects_storylines
   4. 角色弧光 → 合并到粗大纲 character_lines[].direction + 卷纲 character_line_progress[].growth_marker
   5. 伏笔地图 → 保留为可选参考文件（字段格式兼容，自动追加 chunk-XX 的伏笔引用）
   6. 卷纲 → 按需生成（写到 Vx 起始章时自动产出，不需要迁移）

是否执行迁移？（输入"是"开始 / "否"跳过 / "查看 diff"先看具体变化）
```

**迁移风险**：
- 旧 `storylines[].character`（单角色绑定）→ 新 `key_characters[]`：如果旧大纲只有主角单角色推进，迁移后 `key_characters` 也只含主角——后续可手动扩展其他角色推进
- 旧 `角色弧光.yaml` 的 `cross_character_intersections` → 新卷纲 `turning_points[].affects_character_lines`：可能需要重新核对跨角色交点（因为旧文件是按角色分类的，新文件是按转折点分类的）
- 已锁定的伏笔（出现在旧 `伏笔地图.yaml` 但未在新 3 段大纲体现）：自动追加到 chunk 设计的 `must_include` 候选

**回退**：
- 迁移前备份在 `outline/archive-v1.2/<timestamp>/`——任何时候都可手动恢复
- 迁移脚本本身只读 + 写新文件，不修改旧文件
- 如迁移后发现问题，可手动 `cp -r outline/archive-v1.2/<timestamp>/* outline/` 回滚

**何时执行**：
- 工作区是 0.1.2 之前创建的，已写过几章且不想从头开始
- 想用 0.1.3 的 3 段大纲 + 漂移检测，但保留原有伏笔和故事线设计

**何时不执行**：
- 工作区是 0.1.3 新建（没有旧文件）——直接用 `/novel-studio:outline` 创建即可
- 旧大纲文件被手动编辑过且不标准——迁移可能不完整，建议手动迁移

---

### 调整已有大纲

如果用户已有大纲想调整：

```
📐 你想调整大纲的哪一段/层？

- 段 1 粗大纲：
  - 故事线（增删/调整主题、推进者、赌注）
  - 人物线（增删/调整 POV 角色方向、起点/终点状态）
  - 分卷（调整卷数、章节范围、功能、主推线）
- 段 2 卷纲（指定 volume-XX）：
  - storyline_progress / character_line_progress / phase_map / turning_points / volume_end_hook
- 段 3 chunk 设计（指定 chunk-XX）：
  - beats[] / active_storyline / active_character_lines
- 或者直接说你觉得哪里不对
```

**调整原则**：调整只影响相关层面——改一条故事线不会重写全书大纲；改 chunk 中的 beat 不会影响卷纲。Orchestrator 检测到跨段影响时会主动提示用户。

---

### 大纲检查（漂移检测 + 健康度扫描）

```
/novel-studio:outline 检查
```

**段 1 粗大纲检查**：
- 每条故事线是否有头有尾（start→end 完整）
- 每条故事线是否有角色推进（`key_characters` 非空）
- 每条人物线是否有起止状态（start_state + end_state）
- 故事线和人物线是否平衡（避免故事线无人推进 / 人物线游离于故事线外）
- 分卷是否每卷都有主推故事线 + 重点人物线

**段 2 卷纲检查**（指定 volume-XX）：
- storyline_progress 与粗大纲 volumes[] 是否一致
- character_line_progress 与粗大纲 character_focus 是否一致
- turning_points 是否覆盖双维度（affects_storylines + affects_character_lines）
- phase_map 是否有连续 10 章以上同强度（警告风险）

**段 3 chunk 检查**（指定 chunk-XX）：
- beats[] 的 advancing_storyline 是否与 chunk.active_storyline 一致
- beats[] 的 advancing_character_line 是否与 chunk.active_character_lines 一致
- 是否每章恰好一个 chapter_end_anchor: true
- 字数预算（target_words）总和是否在 ±15% 范围内

**漂移检测**（写作过程中的累积漂移）：
- 故事线漂移：每章锁定时 Critic Lite 检查「实际写出的内容是否推进了 active_storyline.direction」
- 人物线漂移：每章锁定时 Critic Lite 检查「POV 角色的行为是否符合 active_character_lines[].direction」

---

## 反模式（禁止）

- ❌ 生成「第1章做什么→第2章做什么→...」的流水账大纲
- ❌ 把伏笔/节拍/弧光/交错钉死到具体章号——应到「第几卷+卷内前/中/后段」粒度
- ❌ 只有主角人物线，没有配角人物线
- ❌ 故事线和人物线互相不关联（故事线无人推进 / 人物线游离于故事线外）
- ❌ 把所有故事线都绑定到主角一个角色（应允许配角/反派参与推进）
- ❌ 全卷匀速——每章都是「推进」功能
- ❌ 不给用户选择，直接生成完整大纲
- ❌ 强制用户做完全部大纲才允许开写——粗大纲（段 1）确认后即可写
- ❌ 用户说「主角和配角X的关系不太对」，你只改了一处却没检查所有交汇点
- ❌ 在 `/novel-studio:outline` 命令中要求生成卷纲或 chunk 设计——它们在写章节时自动生成
- ❌ 在 chunk 设计时不让 Writer 看到任何故事线/人物线方向——必须在交接包中包含 `storyline_direction` + `character_line_direction`