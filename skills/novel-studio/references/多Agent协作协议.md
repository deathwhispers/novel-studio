# 多 Agent 协作协议

> 本文件是创作流水线的宪法。定义 7 个 Agent 的角色、所有权、上下文预算、交接包格式、记忆架构和渐进纰漏规则。每个 Agent 启动时必须先读本文件，确认自己在流水线中的位置和上下游约束。

---

## 一、Agent 定义

### 总览

```
Orchestrator (会话管理 + 流转控制)
     ↓
Architect (Canon 唯一所有者)
     ↓
Story Director (故事状态 + 信息释放策略)
     ↓
Scene Planner (场景约束 + 节拍设计)
     ↓
Writer (正文唯一执行者)
     ↓
Critic (多检查器质量验收)
     ↓
State Manager (状态更新 + 记忆压缩)
     ↓ back to Orchestrator
```

### 1. Orchestrator

| 属性 | 值 |
|------|---|
| 来源 skill | `novel-studio` |
| 角色 | 会话入口，流转控制。不创作，不检查，不更新状态 |
| 所有权 | `90-运行/` 下的进度文件、决策记录、Agent 运行日志 |
| 输入 | 用户意图 + 工作区信号 |
| 输出 | 下一个 Agent 名称 + 交接包 |
| 上下文预算 | ~2K tokens |
| 加载 | `90-运行/当前进度.md` + `90-运行/Agent运行日志.md` + 工作区文件信号 |
| 绝不加载 | 正文/大纲/设定/canon |

**职责**：
- 判断用户意图，选择进入流水线的入口 Agent
- 生成交接包，传递给下游 Agent
- 检查下游 Agent 返回后的状态，决定继续流转还是暂停
- 不在路由层做任何创作、检查或状态修改
- 会话结束时记录 Agent 运行日志

### 2. Architect

| 属性 | 值 |
|------|---|
| 来源 skill | `novel-project` + `novel-worldbuilding` |
| 角色 | Canon 唯一所有者——世界规则、人物设定、硬约束的源头 |
| 所有权 | `00-书核/`、`10-设定/` |
| 输入 | 用户构想 + 已有 canon 文件 |
| 输出 | Canon 文件 + 硬设定 + 不可破坏项清单 |
| 上下文预算 | ~8K tokens |
| 加载 | 用户构想 + 已有 canon + 项目结构 |
| 绝不加载 | 正文/大纲/状态文件 |

**职责**：
- 创建或更新世界规则、人物设定、力量体系、时间线
- 维护「硬设定清单」——下游任何 Agent 都不可违反的规则
- 回答下游 Agent 的 canon 查询（通过 Orchestrator 中转，不直接对话）
- 不接触正文、大纲或读者反馈

### 3. Story Director

| 属性 | 值 |
|------|---|
| 来源 skill | `novel-outline` |
| 角色 | 故事状态唯一所有者——决定为什么写、写什么、释放什么信息 |
| 所有权 | `20-大纲/`、`10-状态/连载状态.md`（写权限） |
| 输入 | Canon（从 Architect）+ 状态文件 + 节拍卡 |
| 输出 | Story Contract（章节功能 + 信息释放策略 + 禁止触碰清单 + 旧线触碰计划） |
| 上下文预算 | ~6K tokens |
| 加载 | Canon 摘要 + 当前卷纲 + 节拍卡 + 状态文件（作者/角色/读者状态） |
| 绝不加载 | 完整正文/所有章节大纲 |

**职责**：
- 决定本章功能（推进/揭示/余震/过渡/高潮）
- 从「作者状态」提取本章禁止触碰清单
- 从「线索追踪表」选择 0-2 条需要轻碰的旧线
- 规划信息释放节奏：本章释放什么、暗示什么
- 输出 Story Contract 给 Scene Planner
- **不设计场景如何执行、不接触具体句子**

### 4. Scene Planner

| 属性 | 值 |
|------|---|
| 来源 skill | `novel-scene-planner`（新建） |
| 角色 | 场景执行设计者——决定这一场怎么演、冲突怎么发生、节奏如何变化 |
| 所有权 | 场景节拍设计 |
| 输入 | Story Contract + 状态文件（视角角色状态） |
| 输出 | Scene Contract（五拍骨架 + 视角约束 + 场景氛围） |
| 上下文预算 | ~4K tokens |
| 加载 | Story Contract + 视角角色状态 + 最近 2 章正文（仅场景结构，不读完整正文）+ voice 样本标签 |
| 绝不加载 | 完整大纲/完整 canon/完整状态文件 |

**职责**：
- 将 Story Director 的「本章功能」翻译为每个场景的五拍骨架（目标→阻碍→变化→意外→新问题）
- 确定主视角、叙述距离、场景空间和环境压力
- 设计冲突推进的具体方式（对抗/误读/隐瞒/试探/环境压力）
- 衔接场景之间的因果链（上一场景的后果如何触发下一场景）
- 输出 Scene Contract 给 Writer
- **不写正文、不释放具体信息、不接触完整大纲**

### 5. Writer

| 属性 | 值 |
|------|---|
| 来源 skill | `novel-writing` |
| 角色 | 正文唯一执行者——在约束内写出可读的句子 |
| 所有权 | `30-正文/` |
| 输入 | Scene Contract + 最近 2 章正文 + voice 样本 + 1-2 份参考片段 |
| 输出 | 正文 + 状态增量标记 |
| 上下文预算 | ~6K tokens |
| 加载 | Scene Contract(~400 tokens) + 最近 2 章正文 + voice 样本 + 参考片段 |
| 绝不加载 | 完整大纲/完整 canon/状态文件/禁止触碰背后的「为什么」 |

**职责**：
- 在 Scene Contract 约束内连续起草
- 不读完整大纲——不知道第 50 章的反转或第 80 章的真相
- 只知道 Scene Contract 说「本章禁止触碰 X、可以释放 Y」
- 每个场景边界执行硬门禁
- 输出正文后标记本章实际发生的变化（状态增量标记）
- **不判断信息释放策略、不决定章尾落点**

### 6. Critic

| 属性 | 值 |
|------|---|
| 来源 skill | `novel-quality` |
| 角色 | 质量门禁唯一裁判——内部执行 5 个 Checker |
| 所有权 | 验收标准 |
| 输入 | 正文 + Scene Contract + Story Contract + 状态文件（约束块） |
| 输出 | Review Report（通过/局部修复/骨架失效 + 各项检查结果） |
| 上下文预算 | ~5K tokens |
| 加载 | 当前章正文 + Scene Contract + Story Contract 约束部分 + AI 味目录 |
| 绝不加载 | 完整 canon/完整大纲/其他章节/完整状态文件 |

**内部 5 个 Checker**（按顺序执行）：

| Checker | 检查内容 | 失败处理 |
|---------|---------|---------|
| Logic Checker | 因果链、连续性、硬设定违反 | 局部修复，骨架问题回 Scene Planner |
| Information Leak Checker | 正文是否触碰 Story Contract 的禁止触碰清单 | 局部移除 + 复查上下文 |
| Character Checker | 人物动机、选择可信度、POV 角色认知边界 | 局部修复 |
| Pace Checker | 场景节拍是否按 Scene Contract 执行、节奏是否断裂 | 标注偏离，不自动修复 |
| Style Checker | AI 味扫描、角色辨识度、voice 漂移 | 标注并给出修复建议 |

**输出 Review Report**：
```text
通过 / 局部修复 / 骨架失效
Logic: 通过 / 失败(原因)
Info Leak: 通过 / 失败(具体泄露项)
Character: 通过 / 失败(具体问题)
Pace: 符合约束 / 偏离(说明)
Style: 通过 / 需修复(N处AI味 / voice漂移)
```

### 7. State Manager

| 属性 | 值 |
|------|---|
| 来源 skill | `novel-state-manager`（新建） |
| 角色 | 状态更新唯一执行者——Critic 验收通过后，更新所有持久化状态 |
| 所有权 | `10-状态/连载状态.md` + 记忆压缩 |
| 输入 | Review Report（必须是通过状态）+ 正文状态增量标记 + 当前状态文件 |
| 输出 | 更新后的状态文件 + 压缩决策 |
| 上下文预算 | ~3K tokens |
| 加载 | Review Report + 状态增量标记 + 当前状态文件 |
| 绝不加载 | 正文/大纲/canon |

**职责**：
- 更新「作者状态」：新秘密加入、已揭示秘密归档
- 更新「角色状态」：各 POV 角色的已知/不知/误判/目标/压力
- 更新「读者状态」：读者已知/未知/猜测方向
- 更新「线索追踪表」：新线索记录、已回收线索标记
- 每 5 章执行记忆压缩：合并冗余、归档已揭示、摘要非活跃线
- 将约束块存档到 `10-状态/导演约束存档/`
- **不判断质量、不修改正文、不决定剧情方向**

---

## 二、交接包格式

每个 Agent 向下游传递时，Orchestrator 生成交接包。交接包是 Agent 启动时的最小上下文锚点，≤500 tokens。

```text
【交接包 — {{上游Agent}} → {{下游Agent}}】

当前章节：第 N 章 {{章节名}}
写作模式：{{商业连载/类型长篇/文学叙事/短篇/探索起草}}

## 传递内容
{{上游 Agent 的核心输出摘要，按下游 Agent 需求裁剪}}

## 状态标记
- 上一章硬门禁：通过 / 未通过(原因)
- 状态文件版本：{{时间戳或版本号}}
- 紧急上下文：{{如果上一章结尾有未解决的直接后果，在此简述}}

## 下游启动指令
- 读取文件：{{下游 Agent 必须加载的文件路径，绝对路径}}
- 禁止加载：{{下游 Agent 绝不能触碰的文件或信息类别}}
- 本次任务：{{一句话任务描述}}

## 上下文预算
- 本次可用：{{下游 Agent 的 token 预算}}
- 当前已用：{{交接包 + 固定开销的估算}}
- 留给任务：{{剩余可用}}
```

**裁剪规则**：
- Orchestrator→Architect：传递用户构想摘要
- Orchestrator→Story Director：传递当前进度 + canon 版本
- Story Director→Scene Planner：Story Contract
- Scene Planner→Writer：Scene Contract
- Writer→Critic：正文路径 + Scene Contract 引用
- Critic→State Manager：Review Report（仅当通过时）
- 任何 Agent→Orchestrator：Agent 完成标记 + 输出文件路径

---

## 三、记忆架构

### 三层记忆模型

```
第一层：持久化状态（跨会话，文件存储）
  ├── 10-状态/连载状态.md        ← 主状态文件（三态+线索）
  ├── 10-状态/卷记忆/第X卷-摘要.md  ← 每卷结束由 State Manager 压缩生成
  └── 10-状态/导演约束存档/        ← 每章 Director 约束存档

第二层：章节记忆（本次流水线内有效）
  ├── Story Contract（Story Director 输出，Scene Planner + Writer + Critic 共用）
  ├── Scene Contract（Scene Planner 输出，Writer + Critic 共用）
  ├── 正文状态增量（Writer 输出，State Manager 消费）
  └── Review Report（Critic 输出，State Manager 消费）

第三层：交接包（Agent 间传递，用完即弃）
  └── 每次 Agent 切换时由 Orchestrator 生成，≤500 tokens
```

### 长期记忆压缩协议（State Manager 每 5 章执行）

**触发条件**：当前章节号 % 5 == 0，或卷末

**压缩操作**：
1. **线索追踪表压缩**：已回收的线索保留一行摘要（章/内容/回收方式），删除详细描述
2. **角色状态压缩**：非 POV 角色的状态合并为一段摘要；POV 角色保留完整状态
3. **读者状态压缩**：已揭示的信息移入「读者已知摘要」，不再逐章展开
4. **卷记忆生成**：生成本卷摘要写入 `10-状态/卷记忆/第X卷-摘要.md`，包含：
   - 本卷关键事件（最多 10 条，每条一行）
   - 本卷揭示的秘密
   - 本卷新增的活跃伏笔
   - 卷末各 POV 角色状态快照
5. **状态文件瘦身**：删除已被卷摘要覆盖的逐章细节，保留当前章和上一章的完整状态

**压缩后状态文件大小**：控制在 500 行以内（含卷记忆摘要引用）

---

## 四、上下文预算总表

| Agent | 预算 | 最大加载量 | 关键约束 |
|-------|------|-----------|---------|
| Orchestrator | 2K | 进度文件 + 日志 | 不创作不检查 |
| Architect | 8K | 全量 canon | 不读正文大纲 |
| Story Director | 6K | Canon 摘要 + 卷纲 + 状态文件 | 不读正文 |
| Scene Planner | 4K | Story Contract + 视角状态 + 2章结构 | 不读完整大纲 |
| Writer | 6K | Scene Contract + 2章正文 + voice + 片段 | 不读大纲 canon |
| Critic | 5K | 正文 + 约束 + AI味目录 | 不读 canon 大纲 |
| State Manager | 3K | Review Report + 增量 + 状态文件 | 不读正文大纲 |

**超预算处理**：任何 Agent 发现所需上下文超出预算时，通过 Orchestrator 请求压缩或裁剪，不允许自行扩大加载范围。

---

## 五、渐进纰漏强制规则

写入每个 Agent 的 SKILL.md，由 Orchestrator 在交接时校验：

1. **Writer 不读完整大纲**。Writer 只通过 Scene Contract 知道本章该写什么、不能碰什么。它不知道第 50 章的反转是什么——只知道「本章禁止触碰的内容里有 X，但不知道 X 为什么被禁」。

2. **Scene Planner 不读完整 canon**。Scene Planner 从 Story Director 接收信息释放策略，不需要知道世界规则的全貌。

3. **Story Director 不读正文**。Story Director 操作的是大纲层和信息层，通过状态文件了解角色和读者状态，不接触具体句子。

4. **Critic 的信息泄漏检查**：对照 Story Contract 的禁止触碰清单逐项搜索正文，不依赖 Critic 自己的「我觉得这里好像泄露了」——必须是清单中的具体项。

5. **State Manager 不判断质量**。State Manager 只在 Critic 通过后才执行更新。Review Report 标记为「未通过」时，State Manager 不启动。

6. **禁止 Agent 间直接对话**。所有跨 Agent 通信通过 Orchestrator 中转。下游 Agent 不能「回问」上游 Agent——如果需要更多信息，回 Orchestrator，由 Orchestrator 决定是否重新调用上游。

---

## 六、Agent 运行日志

Orchestrator 每次流转时记录到 `90-运行/Agent运行日志.md`：

```text
[时间戳] Orchestrator → Story Director | Ch.XX | 交接包已传递
[时间戳] Story Director → Orchestrator | Ch.XX | Story Contract 已生成 | 文件: XXX
[时间戳] Orchestrator → Scene Planner | Ch.XX | 交接包已传递
[时间戳] Scene Planner → Orchestrator | Ch.XX | Scene Contract 已生成 | 文件: XXX
...
[时间戳] State Manager → Orchestrator | Ch.XX | 状态已更新 | 压缩: 是/否
```

用途：断点恢复。Orchestrator 启动时读取最后一条日志，判断流水线停在哪个 Agent，从断点继续。

---

## 七、现有 skill 到 Agent 的映射

| Agent | skill 目录 | 角色标注 |
|-------|-----------|---------|
| Orchestrator | `novel-studio` | 在 SKILL.md 头部标注 `role: orchestrator` |
| Architect | `novel-project` + `novel-worldbuilding` | project 作为入口，worldbuilding 作为 canon 引擎 |
| Story Director | `novel-outline` | 标注 `role: story-director` |
| Scene Planner | `novel-scene-planner` | 新建 |
| Writer | `novel-writing` | 标注 `role: writer` |
| Critic | `novel-quality` | 标注 `role: critic` |
| State Manager | `novel-state-manager` | 新建 |
| （独立） | `novel-market` | 不进入创作流水线，独立调用 |
