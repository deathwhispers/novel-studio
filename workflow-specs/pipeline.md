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

**关键变化（vs 旧版逐段流水线）**：

| 阶段 | 旧版 | 新版 |
|------|------|------|
| 方向确定 | 3-5 轮对话讨论本章方向 | LOOP 一次性展示所有 beat 选项，用户逐个确认（含自定义/跳到/回 LOOP） |
| 写作流程 | 逐段：给选项 → 写200-400字 → 检查 | 节拍内一次写完 200-400 字；节拍间按 chunk_mode 决定停/续 |
| 质量检查 | Critic Lite 整章收尾（Logic/Character/Style） | Critic Lite 三档：segment（单 beat）/ chapter（整章）/ super（整 chunk） |
| 状态源 | `progress.yaml` 的 `chapter_state` + segment 临时状态 | `progress.yaml` 的 `chunk_plan` 块（单一源） |

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

**触发**: `/novel-studio:outline`

```mermaid
flowchart TD
    User["👤 User: /novel-studio:outline"]
    Orchestrator["🎯 Orchestrator<br/>确认操作类型<br/>创建/调整/检查"]

    User --> Orchestrator

    Orchestrator --> Create["创建大纲<br/>五层递进"]
    Orchestrator --> Adjust["调整大纲<br/>定位目标层"]
    Orchestrator --> Review["检查大纲<br/>6项扫描"]

    Create --> Layer1["第一层：全书总纲<br/>核心冲突→故事线→分卷"]
    Layer1 --> Layer2["第二层：逐卷细化<br/>关键节拍→节奏检查"]
    Layer2 --> Layer3["第三层：故事线交错<br/>卷内各段主次线分配"]
    Layer3 --> Layer4["第四层：伏笔布局<br/>埋设→轻碰→回收"]
    Layer4 --> Layer5["第五层：角色弧光<br/>状态变化→催化剂事件"]
    Layer5 --> OutlinerGen["Outliner 写入文件"]
    Adjust --> OutlinerGen
    Review --> OutlinerCheck["Outliner 全面检查"]
    OutlinerCheck --> OutlinerGen
    OutlinerGen --> Done(["✅ 大纲就绪"])
```

**输出文件**: `outline/全书总纲.yaml`、`outline/volumes/`、`outline/故事线交错.yaml`、`outline/伏笔地图.yaml`、`outline/角色弧光.yaml`

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

## 七、工作区升级（upgrade-project）

**触发**: `/novel-studio:upgrade`（检测到 v2 旧结构时）

```mermaid
flowchart TD
    User["👤 User: /novel-studio:upgrade"]
    Orchestrator["🎯 Orchestrator<br/>检测旧版特征 + 备份 + 改名"]

    User --> Orchestrator

    Orchestrator -->|"备份完成"| Rename["🔧 结构改名<br/>• 作品总表→作品核心<br/>• 硬设定→硬规则<br/>• 全书总纲.md→.yaml<br/>• progress.yaml 字段改写"]
    Rename --> Architect["🏗️ Architect<br/><b>内容补全</b><br/>• core 灵魂契约补全<br/>• 硬设定拆分<br/>（作者确认）"]
    Architect --> Outliner["🧭 Outliner<br/><b>大纲重构</b><br/>• 主线/支线→角色故事线<br/>• 卷级规划<br/>（作者确认）"]
    Outliner --> StateManager["📋 StateManager<br/>校验 + 写 schema_version"]
    StateManager --> Done(["✅ 升级完成<br/>state/ 已保留，可续写"])
```

详见 [`workflow-specs/upgrade-project.md`](upgrade-project.md)。

---

## Agent ↔ 流水线对应关系

| Agent | 出现在流水线 |
|-------|-------------|
| Orchestrator | 全部七条 |
| Architect | 初始化、世界观构建、工作区升级（内容补全） |
| Outliner | 大纲设计、工作区升级（大纲重构） |
| ScenePlanner | 修订（场景重设） |
| Writer | 写章节（逐段模式）、修订（全部四种范围） |
| Critic | 写章节（收尾 Lite）、修订（场景重设/局部修复/仅去味）、质量检查 |
| StateManager | 写章节（逐段模式）、初始化、修订、世界观构建、工作区升级（校验） |

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
