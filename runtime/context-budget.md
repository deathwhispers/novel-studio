# 上下文预算表

> 定义每个 Agent 的 token 预算。Agent 通过 Orchestrator 传递的交接包获取所需信息，而非自行加载文件。交接包格式见 `runtime/handoff-schema.md`。

---

## 渐进式披露协议

### 核心原则

每个 Agent 只看到完成任务所需的最小信息集合。Orchestrator 从上游完整输出中裁剪出下游需要的字段，以交接包形式传递。

### 信息分级

| 层级 | 持有者 | 内容 |
|------|--------|------|
| 路由层 | Orchestrator | progress.yaml、agent-log.yaml |
| 决策层 | Director | 状态摘要、卷纲、硬设定摘要 |
| 执行层 | ScenePlanner/Writer/Critic | 场景级信息、正文 |

决策层不加载完整状态文件，执行层不加载上游内部细节。

### 交接包机制

1. 上游 Agent 产出完整输出 → Orchestrator 接收
2. Orchestrator 按 `handoff-schema.md` 中下游 Agent 的 Brief 格式裁剪
3. 大文件（正文、voice 样本）传递路径而非内容，由目标 Agent 自行读取
4. 每个 Brief 包含 `must_not_read` 清单，明确禁止自行加载额外文件

### Token 估算规则

- 中文正文约 1.5 tokens/字，英文约 1 token/字
- YAML 约 0.8 tokens/字
- 交接包自身的 YAML 结构约 0.5K tokens

---

## 总览

| Agent | 预算 | 输入来源 | 核心约束 |
|-------|------|---------|---------|
| Orchestrator | ~2K | progress.yaml + agent-log.yaml | 不创作、不检查、不修改状态 |
| Architect | ~8K | 用户构想 + canon + 品类配方 | 不读正文/大纲/状态文件 |
| Director | ~4K | DirectorBrief（状态摘要） | 不读正文、不读完整状态文件 |
| ScenePlanner | ~3K | ScenePlannerBrief（Story Contract + 结构） | 不读完整大纲/完整 canon |
| Writer | ~4.5K | WriterBrief（scenes + 约束 + 章尾） + 最近2章正文 | 不读大纲/canon/状态文件/完整 Scene Contract |
| Critic | ~3.5K | CriticBrief（合并检查清单） + 当前章正文 + AI味目录 | 不读完整 canon/完整大纲/其他章节 |
| StateManager | ~2.5K | StateManagerBrief（Review Report + state_delta） + 全部状态文件 | 不读正文/大纲/canon |

---

## 各 Agent 加载明细

### Orchestrator（~2K tokens）

**输入来源**：无交接包。直接读取路由层文件。

**必须加载**：
- `state/progress.yaml`（约200 tokens）
- `state/agent-log.yaml`（最后5条，约300 tokens）

**信息裁剪职责**（新增）：
- 收到上游 Agent 完整输出后，按 `runtime/handoff-schema.md` 裁剪为下游 Brief
- 不直接透传上游输出——移除下游不需要的字段

**按需加载**（确认意图后）：
- 对应的 Workflow 文件（约500 tokens）
- 品类配方索引（仅 init 时，约200 tokens）

**绝不加载**：
- 任何正文内容
- 任何大纲内容
- 任何设定内容
- 任何状态文件的详细内容（author/reader/character/foreshadow）

---

### Architect（~8K tokens）

**输入来源**：不使用 Brief 格式。在 init-project 和 worldbuilding 两条流水线中，Orchestrator 直接传递用户构想。

**必须加载**：
- 用户构想摘要（从 Orchestrator 交接包，约300 tokens）
- 已有 canon 文件（`setting/` 下全部，约3-5K tokens）
- 品类配方 recipe.md（如适用，约1K tokens）

**按需加载**：
- 角色文件（逐个加载，每个约500 tokens）
- 世界观文件（约1K tokens）
- 力量体系文件（约1K tokens）

**绝不加载**：
- `chapters/` 任何文件
- `outline/` 任何文件
- `state/` 任何文件

**超预算处理**：
- 角色超过 8 个时，只加载 POV 角色的完整档案，其他角色仅加载 ID + 当前状态摘要

---

### Director（~4K tokens）

**输入来源**：`DirectorBrief`（`runtime/handoff-schema.md` 第一节）

Director 不再自行加载完整状态文件。Orchestrator 从状态文件中提取摘要后放入 DirectorBrief。

**交接包内容**（~2.5K tokens）：
- `user_intent` / `chapter_number` / `genre`
- `state_summary`：
  - `secrets`：author.yaml 中 status != revealed 的秘密（仅 id + title + planned_reveal_chapter）
  - `open_questions`：reader.yaml 中最近 5 条未解答问题
  - `reading_tension`：四项指标数值
  - `pov_characters`：POV 角色的 knowledge.unknown + constraints
  - `active_threads`：foreshadow.yaml 中 active 伏笔（id + content + priority + last_touched）
- `must_read`：卷纲路径、硬设定路径、品类 rhythm 路径

**交接包外自行加载**（仅路径指定的文件）：
- 当前卷纲（约1K tokens）
- 硬设定摘要（约300 tokens）
- 品类配方 rhythm.md（约500 tokens，如适用）

**绝不加载**：
- `chapters/` 任何文件
- `state/` 完整状态文件（摘要已在交接包中）

**超预算处理**：
- `active_threads` 超过 10 条时，Orchestrator 只提取 high priority 的伏笔

---

### ScenePlanner（~3K tokens）

**输入来源**：`ScenePlannerBrief`（`runtime/handoff-schema.md` 第二节）

ScenePlanner 收到完整 Story Contract + POV 角色摘要 + 最近章节结构。不加载完整状态文件。

**交接包内容**（~1.5K tokens）：
- `story_contract`：完整 Story Contract（~1K，ScenePlanner 需要全部字段设计场景）
- `pov_character_brief`：POV 角色 name + current_state + speech_pattern + mannerisms
- `recent_chapters_structure`：最近 2 章的章号/场景数/每场景功能/字数（不含正文）

**交接包外自行加载**：
- 品类配方 rhythm.md 场景轮换部分（约300 tokens，如适用）

**绝不加载**：
- `chapters/` 正文全文
- 完整大纲（只知道本章功能，不知道后续章节）
- 完整 canon（只知道本章涉及的角色和规则）
- 完整状态文件

**超预算处理**：
- 最近 2 章结构超出 500 tokens → 只保留最近 1 章结构

---

### Writer（~4.5K tokens）

**输入来源**：`WriterBrief`（`runtime/handoff-schema.md` 第三节）

Writer 不再加载完整 Scene Contract。交接包中只包含 Writer 实际使用的字段。

**交接包内容**（~1.5K tokens）：
- `scenes`：每场景的 id/function/pov/narrative_distance/environment/environment_pressure/five_beats
- `writer_constraints`：must_preserve + must_avoid
- `chapter_end`：hook + reader_question
- `must_read`：最近 2 章正文路径、voice 样本路径

**交接包外自行加载**（路径由交接包指定）：
- 最近 2 章正文全文（约3-4K tokens）
- voice 样本（角色的具体对话和叙述片段，约500 tokens）
- 1-2 份参考片段（从 `snippets/` 匹配，约300 tokens）

**按需加载**（写中调用，不预加载）：
- 单个 narrative skill（每次只加载 1 个，约500 tokens）
- 品类 tropes 参考（约300 tokens）

**绝不加载**：
- Scene Contract 完整文件（所需字段已在交接包中）
- 完整大纲（不知道第 50 章的反转）
- 完整 canon（不知道世界规则的全貌）
- 状态文件（不知道作者秘密、读者猜测、伏笔全貌）

**超预算处理**：
- 最近 2 章正文超出 4K tokens 时，只加载最近 1 章 + 上一章最后 500 字
- 参考片段超过 2 份时，只加载最匹配的 1 份

---

### Critic（~3.5K tokens）

**输入来源**：`CriticBrief`（`runtime/handoff-schema.md` 第四节）

Critic 不再分别加载 Scene Contract + Story Contract + character.yaml。收到一份合并的 CriticBrief 检查清单。

**交接包内容**（~1K tokens）：
- `chapter_text`：当前章正文路径
- `forbid_touch`：禁止触碰清单（从 Story Contract 提取）
- `hard_canon_checklist`：硬设定检查清单（从 setting/硬设定.yaml 精简）
- `pov_constraints`：POV 角色的 cannot_know + cannot_do
- `genre_taboos`：品类禁忌（如适用）
- `ai_flavor_catalog`：AI 味目录路径

**交接包外自行加载**（路径由交接包指定）：
- 当前章正文全文（约3-4K tokens）
- AI 味目录 `references/ai-flavor-catalog.md`（约800 tokens）

**绝不加载**：
- Scene Contract 完整文件
- Story Contract 完整文件
- 完整 canon
- 完整大纲
- 其他章节正文
- 完整状态文件

---

### StateManager（~2.5K tokens）

**输入来源**：`StateManagerBrief`（`runtime/handoff-schema.md` 第五节）

StateManager 是唯一需要加载完整状态文件的 Agent。交接包中传递 Review Report 和 state_delta。

**交接包内容**（~0.5K tokens）：
- `review_report`：完整 Review Report
- `state_delta`：完整 state_delta
- `must_read`：4 个状态文件路径 + progress.yaml

**交接包外自行加载**（路径由交接包指定）：
- `state/author.yaml`（约500 tokens）
- `state/reader.yaml`（约500 tokens）
- `state/character.yaml`（约1K tokens）
- `state/foreshadow.yaml`（约500 tokens）
- `state/progress.yaml`（约200 tokens）

**按需加载**（每 5 章压缩时）：
- 卷记忆摘要模板（约200 tokens）

**绝不加载**：
- `chapters/` 任何文件
- `outline/` 任何文件
- `setting/` 任何文件

---

## 预算执行规则

1. **交接包优先**：Agent 启动时先读取交接包。交接包中已有的信息，不允许自行加载。
2. **must_not_read 是硬约束**：每个 Brief 包含禁止加载清单，Agent 不得违反。
3. **按需加载**：交接包中标记为路径的文件在使用时读取，不在 Agent 启动时预加载。
4. **超预算检测**：Agent 启动后估算已用 tokens，若剩余不足以完成核心任务 → 报告 Orchestrator → Orchestrator 决定裁剪方案。
5. **禁止自行扩大**：任何 Agent 发现信息不足时，不能自行加载更多文件——必须通过 Orchestrator 请求。
6. **上下文释放**：Agent 完成输出后上下文自动释放（每个 Agent 是独立调用）。
