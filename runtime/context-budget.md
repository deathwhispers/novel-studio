# 上下文预算表

> 定义每个 Agent 的 token 预算。Agent 启动时必须遵守。超出预算时通过 Orchestrator 请求压缩或裁剪，不允许自行扩大加载范围。

---

## 总览

| Agent | 预算 | 最大加载量 | 核心约束 |
|-------|------|-----------|---------|
| Orchestrator | ~2K | progress.yaml + agent-log.yaml | 不创作、不检查、不修改状态 |
| Architect | ~8K | 全量 canon + 品类配方 | 不读正文/大纲/状态文件 |
| Director | ~6K | Canon 摘要 + 卷纲 + 全部状态文件 | 不读正文 |
| Scene Planner | ~4K | Story Contract + POV 角色状态 + 最近2章结构 | 不读完整大纲/完整 canon |
| Writer | ~6K | Scene Contract + 最近2章正文 + voice 样本 + 1-2参考片段 | 不读大纲/canon/状态文件 |
| Critic | ~5K | 当前章正文 + Scene Contract + Story Contract约束 + AI味目录 | 不读 canon/完整大纲/其他章节 |
| State Manager | ~3K | Review Report + 状态增量标记 + 全部状态文件 | 不读正文/大纲/canon |

---

## 各 Agent 加载明细

### Orchestrator（~2K tokens）

**必须加载**：
- `state/progress.yaml`（约200 tokens）
- `state/agent-log.yaml`（最后5条，约300 tokens）

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

### Director（~6K tokens）

**必须加载**：
- Canon 摘要（从 Architect 产出，约500 tokens）
- 当前卷纲（约1K tokens）
- `state/author.yaml`（约500 tokens）
- `state/reader.yaml`（约500 tokens）
- `state/character.yaml`（仅 POV 角色，约1K tokens）
- `state/foreshadow.yaml`（仅活跃伏笔，约500 tokens）

**按需加载**：
- 品类配方 rhythm.md（约500 tokens）
- 节拍卡模板（约300 tokens）

**绝不加载**：
- `chapters/` 任何文件（Director 不读正文，通过状态文件了解故事进展）

**超预算处理**：
- 活跃伏笔超过 10 条时，只加载 high priority
- 角色超过 5 个 POV 时，只加载当前卷涉及的 POV

---

### Scene Planner（~4K tokens）

**必须加载**：
- Story Contract（从 Director 产出，约400 tokens）
- POV 角色状态（从 character.yaml 提取当前章视角角色，约300 tokens）
- 最近 2 章正文的**结构信息**（章号/场景数/每场景功能/字数，不加载正文内容，约500 tokens）

**按需加载**：
- voice 样本标签（角色说话方式概括，约200 tokens）
- 品类配方 rhythm.md 的场景类型轮换部分（约300 tokens）

**绝不加载**：
- 完整大纲（只知道本章功能，不知道后续章节）
- 完整 canon（只知道本章涉及的角色和规则）
- 状态文件的详细内容

**超预算处理**：
- 最近 2 章正文只能加载结构，不能加载正文全文

---

### Writer（~6K tokens）

**必须加载**：
- Scene Contract（从 Scene Planner 产出，约400 tokens）
- 最近 2 章正文**全文**（约3-4K tokens）
- voice 样本（角色的具体对话和叙述片段，约500 tokens）
- 1-2 份参考片段（从 `snippets/` 匹配，约300 tokens）

**按需加载**（写中调用，不预加载）：
- 单个 narrative skill（dialogue/scene-render/emotion-payoff/pov-control，每次只加载 1 个，约500 tokens）
- 品类 tropes 参考（约300 tokens）

**绝不加载**：
- 完整大纲（不知道第 50 章的反转）
- 完整 canon（不知道世界规则的全貌）
- 状态文件（不知道作者秘密、读者猜测、伏笔全貌）
- Scene Contract 中「禁止触碰」项背后的「为什么」

**超预算处理**：
- 最近 2 章正文超出 4K tokens 时，只加载最近 1 章 + 上一章最后 500 字
- 参考片段超过 2 份时，只加载最匹配的 1 份

---

### Critic（~5K tokens）

**必须加载**：
- 当前章正文全文（约3-4K tokens）
- Scene Contract（约400 tokens）
- Story Contract 的约束部分（禁止触碰清单 + 信息释放计划，约300 tokens）
- AI 味目录（`references/ai-flavor-catalog.md`，约800 tokens）

**按需加载**（Checker 执行时分别加载）：
- 硬设定摘要（Logic Checker 用，约300 tokens）
- character.yaml POV 角色认知（Character Checker 用，约300 tokens）
- 品类配方禁忌列表（Style Checker 用，约200 tokens）

**绝不加载**：
- 完整 canon
- 完整大纲
- 其他章节正文
- 完整的 author.yaml / reader.yaml / foreshadow.yaml

---

### State Manager（~3K tokens）

**必须加载**：
- Review Report（从 Critic 产出，约300 tokens）
- 正文状态增量标记（从 Writer 产出，约200 tokens）
- 当前 `state/` 下全部 4 个文件（author/reader/character/foreshadow，约1.5-2K tokens）

**按需加载**（每 5 章压缩时）：
- 卷记忆摘要模板（约200 tokens）

**绝不加载**：
- `chapters/` 任何文件
- `outline/` 任何文件
- `setting/` 任何文件

---

## 预算执行规则

1. **预加载 vs 按需加载**：Agent 启动时只加载「必须加载」项。按需加载项在使用时读取，用完后从上下文中释放。
2. **超预算检测**：Agent 在加载完「必须加载」项后估算已用 tokens，若剩余不足以完成核心任务 → 报告 Orchestrator → Orchestrator 决定裁剪方案。
3. **禁止自行扩大**：任何 Agent 发现信息不足时，不能自行加载更多文件——必须通过 Orchestrator 请求，由 Orchestrator 判断是否加载以及加载什么。
4. **上下文释放**：Agent 完成输出后，在交接包中声明「已释放上下文」，下游 Agent 从头加载自己的上下文。
5. **Token 估算**：中文正文约 1.5 tokens/字，英文约 1 token/字，YAML 约 0.8 tokens/字。
