# 流水线定义

> 本文档是 novel-studio 所有 Agent 流水线的**唯一权威定义**。
> 每个 Agent 在自己的文件中引用本文档，不自行描述流水线位置。

---

## 一、写章节（write-chapter）

**触发**: `/novel-studio:write <N>` | `/novel-studio:write next`

**当前模式**：节拍批量确认 LOOP。详见 [`workflow-specs/write-chapter.md`](write-chapter.md)。

```mermaid
flowchart TD
    User["👤 User"]
    Orchestrator["🎯 Orchestrator<br/>工作区检测 + chunk 加载"]

    User --> Orchestrator

    Orchestrator --> Loop0["阶段 0：节拍 LOOP<br/>逐个 beat 展示选项 → 用户批量确认<br/>→ 选 chunk_mode"]
    Loop0 --> Write1["阶段 1：节拍驱动写作<br/>Writer 按 WriterBrief-Beat<br/>节拍内连续写 200-400 字"]
    Write1 --> Check{"chunk_mode?"}
    Check -->|"segment"| BeatReview["每 beat 写完停下检查"]
    Check -->|"chapter/super"| Auto["连续写完本粒度内所有 beat"]
    BeatReview --> Write1
    Auto --> CriticLite["阶段 2：Critic Lite<br/>segment/chapter/super 三档"]
    CriticLite --> Lock["阶段 3：用户锁定<br/>Writer 汇总 state_delta"]
    Lock --> StateManager["阶段 4：StateManager<br/>章节事务：+字数 +章节数<br/>不改 confirmed_beats"]
    StateManager --> NextChapter{"当前章 =<br/>chunk 最后一章?"}
    NextChapter -->|"否"| User
    NextChunk["否 → User 写下一章"] --> User
    NextChapter -->|"是"| ChunkClose["阶段 5：chunk 收尾事务<br/>archive + 清空 chunk_plan"]
    ChunkClose --> Completed(["✅ chunk LOCKED"])
```

**关键设计**：

| 阶段 | 实现 |
|------|------|
| 方向确定 | LOOP 一次性展示所有 beat 选项，用户逐个确认（含自定义/跳到/回 LOOP） |
| 写作流程 | 节拍内一次写完 200-400 字；节拍间按 chunk_mode 决定停/续 |
| 质量检查 | Critic Lite 三档：segment（单 beat）/ chapter（整章）/ super（整 chunk） |
| 状态源 | `progress.yaml` 的 `chunk_plan` 块（单一源） |

**交接包流转**（节拍模式）：
| 步骤 | 交接包 |
|------|--------|
| Orchestrator → Writer（节拍） | WriterBrief-Beat（current_beat + 已锁方向 + 约束 + 不传 chunk 文件路径） |
| Writer → Orchestrator（beat 完成） | writer_beat_output（节拍 ID + 正文 + 字数 + hard_gate） |
| Orchestrator → Critic（Lite） | CriticBrief-Lite（mode: segment/chapter/super + 正文路径 + 连续性 + beat_plan） |
| Critic → Orchestrator | lite_report（通过/就地修/用户自决） |
| Orchestrator → StateManager | StateManagerBrief（state_delta + 锁定确认） |

---

## 二、初始化项目（init-project）

**触发**: `/novel-studio:init`

```mermaid
flowchart TD
    User["👤 User: /novel-studio:init"]
    Orchestrator["🎯 Orchestrator<br/>多轮确认"]
    Architect["🏗️ Architect<br/><b>创建骨架</b><br/>• core/ + setting/<br/>• 按品类配方初始化设定<br/>• 生成硬规则 + 角色档案"]
    StateManager["📋 StateManager<br/><b>初始化状态</b><br/>• progress.yaml (chapter=0)<br/>• author / reader / character<br/>• foreshadow / agent-log"]
    Done(["✅ 项目就绪"])

    User --> Orchestrator
    Orchestrator -->|"品类/主角/篇幅/模式 已确认"| Architect
    Architect -->|"骨架创建完成"| StateManager
    StateManager --> Done
```

---

## 三、修订章节（revise-chapter）

**触发**: `/novel-studio:revise <N>`

```mermaid
flowchart TD
    User["👤 User: /novel-studio:revise N"]
    Orchestrator["🎯 Orchestrator<br/>确认修订范围"]

    User --> Orchestrator

    Orchestrator --> FullRewrite["全文重写"]
    Orchestrator --> SceneReset["场景重设"]
    Orchestrator --> LocalFix["局部修复"]
    Orchestrator --> DeFlavor["仅去味"]

    FullRewrite -->|"等同 write-chapter 逐段"| FR_User["用户对话定方向 → 逐段写作<br/>→ 锁定 → StateManager"]

    SceneReset -->|ScenePlanner 重排场景| SR_Flow["ScenePlanner → Writer →<br/>Critic → StateManager"]

    LocalFix -->|"跳过 ScenePlanner<br/>Writer 限制修改范围"| LF_Flow["Writer → Critic →<br/>StateManager"]

    DeFlavor -->|"跳过 ScenePlanner<br/>Critic 仅 Style Checker"| DF_Flow["Writer → Critic →<br/>StateManager"]
```

修订范围判断与流程的完整定义见 [`workflow-specs/revise-chapter.md`](revise-chapter.md)。

---

## 四、世界观构建（worldbuilding）

**触发**: `/novel-studio:world`

```mermaid
flowchart TD
    User["👤 User: /novel-studio:world"]
    Orchestrator["🎯 Orchestrator<br/>确认构建范围"]
    Architect["🏗️ Architect<br/><b>创建/更新 canon</b><br/>• 新增角色档案<br/>• 扩展世界观/力量体系<br/>• 更新硬规则清单"]
    StateManager["📋 StateManager<br/>同步 character.yaml<br/>更新 agent-log"]
    Done(["✅ 报告用户"])

    User --> Orchestrator
    Orchestrator -->|"添加角色/补设定/修冲突"| Architect
    Architect -->|"canon 已更新"| StateManager
    StateManager --> Done
```

---

## 五、大纲设计（outline）

**触发**: `/novel-studio:outline [--auto]`

```mermaid
flowchart TD
    User["👤 User: /novel-studio:outline"]
    Orchestrator["🎯 Orchestrator<br/>确认操作类型<br/>创建/调整/检查"]

    User --> Orchestrator

    Orchestrator --> Create["创建大纲<br/>3 段递进"]
    Orchestrator --> Adjust["调整大纲<br/>定位目标段"]
    Orchestrator --> Review["检查大纲<br/>漂移检测 + 健康度扫描"]

    Create --> Stage1["段 1：粗大纲（必做）<br/>核心冲突 → 故事线+人物线 → 分卷粗规划"]
    Stage1 --> OutlinerGen["Outliner 写入<br/>outline/全书总纲.yaml"]

    %% 段 2 和段 3 在写章节时按需生成（不通过 outline 命令）
    Stage1 -.->|"开写"| Write["✍️ /novel-studio:write N"]
    Write -.->|"写到 Vx 起始章"| Stage2Gen["Orchestrator 检测卷纲缺失<br/>→ Outliner 产出 volume-XX.yaml<br/>（对用户透明）"]
    Stage2Gen -.->|"继续写"| Stage3Gen["Orchestrator 检测 chunk 起始<br/>→ Outliner 产出 chunk-XX.yaml<br/>（对用户透明）"]

    Adjust --> Stage1
    Adjust --> Stage2Adjust["调整某 volume-XX"]
    Adjust --> Stage3Adjust["调整某 chunk-XX"]

    Review --> OutlinerCheck["Outliner 扫描 + Critic Lite 漂移检测"]
    OutlinerCheck --> UserDecision["用户决定修复哪些"]
    UserDecision --> Adjust

    OutlinerGen --> Done(["✅ 粗大纲就绪<br/>可开写；卷纲+chunk 写章节时按需生成"])
```

**输出文件**:
- 段 1（必做）：`outline/全书总纲.yaml`（含故事线 + 人物线 + 分卷粗规划 + 交汇点）
- 段 2（按需）：`outline/volumes/volume-XX.yaml`（写到该卷时自动生成）
- 段 3（按需）：`outline/chunks/chunk-XX.yaml`（写到新 chunk 时自动生成）
- 段 4（可选参考）：`outline/伏笔地图.yaml`（保留为可选文件，不强制）

详见 [`workflow-specs/outline.md`](outline.md)。

---

## 六、质量检查（check）

**触发**: `/novel-studio:check <N>`

```mermaid
flowchart LR
    User["👤 User: /novel-studio:check N"]
    Orchestrator["🎯 Orchestrator<br/>加载章节路径"]
    Critic["🔍 Critic<br/><b>5 Checker 只读扫描</b><br/>• 产出 Review Report<br/>• 不触发修复<br/>• 不更新状态"]
    Done(["📊 仅报告，不修改任何文件"])

    User --> Orchestrator
    Orchestrator --> Critic
    Critic --> Done
```

---

## Agent ↔ 流水线对应关系

| Agent | 出现在流水线 |
|-------|-------------|
| Orchestrator | 全部六条 |
| Architect | 初始化、世界观构建 |
| Outliner | 大纲设计（创建/调整/检查）+ **写章节按需生成卷纲（写到 Vx 起始章）+ 按需生成 chunk 设计（写到新 chunk 起始）** |
| ScenePlanner | 修订（场景重设） |
| Writer | 写章节（节拍 LOOP）、修订（全部四种范围） |
| Critic | 写章节（收尾 Lite 三档 + 新增故事线漂移 + 人物线漂移 2 个 Checker）、修订（场景重设/局部修复/仅去味）、质量检查 |
| StateManager | 写章节（节拍 LOOP）、初始化、修订、世界观构建 |

---

## 关键约束

1. **Agent 不自选后继**: 下一步由 workflow 定义和用户确认决定，不由 Agent 推荐
2. **Orchestrator 是唯一中转站**: Agent 之间不直接通信，所有信息经 Orchestrator 传递
3. **StateManager 是大状态唯一写入口**: 其他 Agent 只标记增量（state_delta），不直接写 `state/` 大状态文件（author/reader/character/foreshadow）。StateManager 同时维护事务版本（progress.state_version + transaction-log.yaml）
4. **Writer 不知道大纲全貌**：渐进披露，Writer 只知道当前 beat 的约束和禁止触碰清单（节拍模式） / 当前段的 Scene Contract（修订模式）
5. **交接包裁剪**: Orchestrator 按 `runtime/handoff-schema.md` 裁剪交接包，下游 Agent 只收到所需字段
6. **节拍模式不依赖 ScenePlanner 和全量 Critic**：写章节由 LOOP + 节拍驱动，ScenePlanner 仅在修订使用；Critic 在节拍/整章/整 chunk 收尾以 Lite 模式兜底（无 Scene Contract，不查信息泄漏）
7. **状态更新是版本化事务**: StateManager 每次更新递增 `state_version`、记 transaction-log；写前核对事务号。定义见 `runtime/state-schema.md` 第八节

---

## 交接包类型对照

每条流水线的 Agent 间传递使用专属交接包格式：

| 流转 | 交接包类型 | 说明 |
|------|-----------|------|
| Orchestrator → ScenePlanner | ScenePlannerBrief | 修订目标 + 现有章节结构 |
| Orchestrator → Writer | WriterBrief | scenes/five_beats + 约束 + 章尾落点 |
| Orchestrator → Critic | CriticBrief | 合并检查清单（forbid_touch + canon + pov） |
| Orchestrator → Critic（Lite） | CriticBrief-Lite | 正文路径 + 连续性上下文（写章节收尾） |
| Orchestrator → StateManager | StateManagerBrief | Review Report + state_delta |
| Orchestrator → Architect | 直接传递用户构想 | 不使用 Brief 格式（仅 init/worldbuilding） |

完整字段定义见 `runtime/handoff-schema.md`。
