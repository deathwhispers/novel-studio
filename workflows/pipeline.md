# 流水线定义

> 本文档是 novel-studio 所有 Agent 流水线的**唯一权威定义**。
> 每个 Agent 在自己的文件中引用本文档，不自行描述流水线位置。

---

## 一、写章节（write-chapter）

**触发**: `/novel-studio:write <N>` | `/novel-studio:write next`

**当前模式**：逐段写作 + 用户协作。详见 [`workflows/write-chapter.md`](write-chapter.md)。

```mermaid
flowchart TD
    User["👤 User"]
    Orchestrator["🎯 Orchestrator<br/>状态回顾 + 方向讨论"]

    User --> Orchestrator

    Orchestrator --> Phase1["第一阶段：确认本章方向<br/>报告状态 → 2-3个方向选项 → 用户选择 → 提炼节拍"]
    Phase1 --> Phase2["第二阶段：逐段写作循环<br/>每段：给选项 → 用户选 → Writer写200-400字 → 用户检查/纠偏"]
    Phase2 --> Phase3["第三阶段：整章收尾<br/>拼接 → 排版/AI味自检 → 锁定"]

    Phase3 --> Summarize["📊 汇总 state_delta<br/>Writer 整章级别状态变更"]
    Summarize --> StateManager["📋 StateManager<br/>更新全部状态文件"]
    StateManager --> Completed(["✅ COMPLETED<br/>报告用户"])
```

**关键变化（vs 旧版自动流水线）**：

| 阶段 | 旧版 | 新版 |
|------|------|------|
| 方向确定 | Director 生成 Story Contract | 用户对话替代（3-5 轮方向讨论） |
| 结构设计 | ScenePlanner 生成 Scene Contract | 用户对话替代（每段前给选项选择推进方向） |
| 正文写作 | Writer 一次性写完整章 | Writer 逐段写，每段 200-400 字，写完就停 |
| 质量检查 | Critic 5 Checker 全量检查 | 收尾阶段 Writer 轻量自检（排版+AI味），用户确认 |
| 状态更新 | StateManager（Critic 通过后） | StateManager（用户锁定章节后，Writer 汇总 state_delta） |

**交接包流转**（逐段模式简化）：
| 步骤 | 交接包 |
|------|--------|
| Orchestrator → Writer（逐段） | 用户选择的推进方向 + 已写段落上下文 |
| Writer → Orchestrator（章尾） | 整章正文 + state_delta 汇总 |
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

    FullRewrite -->|"完整流程"| FR_Director["Director → ScenePlanner →<br/>Writer → Critic → StateManager"]

    SceneReset -->|"跳过 Director"| SR_Flow["ScenePlanner → Writer →<br/>Critic → StateManager"]

    LocalFix -->|"跳过 Director + ScenePlanner<br/>Writer 限制修改范围"| LF_Flow["Writer → Critic →<br/>StateManager"]

    DeFlavor -->|"跳过 Director + ScenePlanner<br/>Critic 仅 Style Checker"| DF_Flow["Writer → Critic →<br/>StateManager"]
```

| 用户说 | 修订范围 | 跳过 |
|--------|---------|------|
| 「重写第X章」「全部重写」 | 全文重写 | 无 |
| 「节奏不对」「场景结构有问题」 | 场景重设 | Director |
| 「有几处写得不好」「对话修一下」 | 局部修复 | Director, ScenePlanner |
| 「AI味太重」「去味」 | 仅去味 | Director, ScenePlanner |

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

详见 [`workflows/outline.md`](outline.md)。

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

## 七、项目迁移（migrate-project）

**触发**: `/novel-studio:migrate <现有目录路径>`

```mermaid
flowchart TD
    User["👤 User: /novel-studio:migrate path"]
    Orchestrator["🎯 Orchestrator<br/>扫描章节文件 + 工作区重组"]

    User --> Orchestrator

    subgraph BatchAnalysis["步骤2：分批分析（Archivist × N）"]
        Archivist1["📖 Archivist 批次1<br/>5章 → per-batch-extraction.yaml"]
        Archivist2["📖 Archivist 批次2<br/>5章 → per-batch-extraction.yaml"]
        ArchivistN["📖 Archivist 批次N<br/>5章 → per-batch-extraction.yaml"]
    end

    Orchestrator -->|"重组完成"| Archivist1
    Archivist1 -->|"前批摘要"| Archivist2
    Archivist2 -->|"...前批摘要"| ArchivistN

    ArchivistN -->|"N份提取结果"| Architect["🏗️ Architect<br/><b>合成归档</b><br/>• 角色去重合并<br/>• 伏笔候选升级<br/>• 硬规则合并<br/>• 品类确认<br/>→ migration-extraction.yaml"]

    Architect -->|"提取结果"| OrchestratorConfirm["🎯 Orchestrator<br/><b>多轮作者确认</b><br/>• 角色确认+补充<br/>• 伏笔确认<br/>• 秘密收集<br/>• 大纲导入"]

    OrchestratorConfirm -->|"确认完毕"| ArchGen["🏗️ Architect<br/>写入 setting/ 全部文件"]
    OrchestratorConfirm -->|"确认完毕"| StateGen["📋 StateManager<br/>写入 state/ 全部文件"]

    ArchGen --> Done(["✅ 迁移完成<br/>后续可使用 /novel-studio:write"])
    StateGen --> Done
```

详见 [`workflows/migrate-project.md`](migrate-project.md)。

---

## 八、工作区升级（upgrade-project）

**触发**: `/novel-studio:upgrade`（检测到 v2 旧结构时）

```mermaid
flowchart TD
    User["👤 User: /novel-studio:upgrade"]
    Orchestrator["🎯 Orchestrator<br/>检测旧版特征 + 备份 + 改名"]

    User --> Orchestrator

    Orchestrator -->|"备份完成"| Rename["🔧 结构改名<br/>• 作品总表→作品核心<br/>• 硬设定→硬规则<br/>• progress.yaml 字段改写"]
    Rename --> Architect["🏗️ Architect<br/><b>内容补全</b><br/>• core 灵魂契约补全<br/>• 硬设定拆分<br/>（作者确认）"]
    Architect --> StateManager["📋 StateManager<br/>校验 + 写 schema_version"]
    StateManager --> Done(["✅ 升级完成<br/>state/ 已保留，可续写"])
```

详见 [`workflows/upgrade-project.md`](upgrade-project.md)。

---

## Agent ↔ 流水线对应关系

| Agent | 出现在流水线 |
|-------|-------------|
| Orchestrator | 全部八条 |
| Architect | 初始化、世界观构建、项目迁移（合成归档）、工作区升级（内容补全） |
| Archivist | 项目迁移（分批分析）——迁移完成后不再使用 |
| Outliner | 大纲设计 |
| Director | 修订（全文重写） |
| ScenePlanner | 修订（全文重写/场景重设） |
| Writer | 写章节（逐段模式）、修订（全部四种范围） |
| Critic | 修订（全部四种范围）、质量检查 |
| StateManager | 写章节（逐段模式）、初始化、修订、世界观构建、项目迁移（文件生成）、工作区升级（校验） |

---

## 关键约束

1. **Agent 不自选后继**: 下一步由 workflow 定义和用户确认决定，不由 Agent 推荐
2. **Orchestrator 是唯一中转站**: Agent 之间不直接通信，所有信息经 Orchestrator 传递
3. **StateManager 是大状态唯一写入口**: 其他 Agent 只标记增量（state_delta），不直接写 `state/` 大状态文件（author/reader/character/foreshadow）
4. **Writer 不读大纲**: 渐进披露，Writer 只知道当前段的约束和禁止触碰清单
5. **交接包裁剪**: Orchestrator 按 `runtime/handoff-schema.md` 裁剪交接包，下游 Agent 只收到所需字段
6. **逐段模式不依赖 Director/ScenePlanner/Critic**: 写章节由用户对话驱动，这三个 Agent 仅在修订流程中使用

---

## 交接包类型对照

每条流水线的 Agent 间传递使用专属交接包格式：

| 流转 | 交接包类型 | 说明 |
|------|-----------|------|
| Orchestrator → Director | DirectorBrief | 状态摘要（非完整状态文件） |
| Orchestrator → ScenePlanner | ScenePlannerBrief | 完整 Story Contract + 结构信息 |
| Orchestrator → Writer | WriterBrief | scenes/five_beats + 约束 + 章尾落点 |
| Orchestrator → Critic | CriticBrief | 合并检查清单（forbid_touch + canon + pov） |
| Orchestrator → StateManager | StateManagerBrief | Review Report + state_delta |
| Orchestrator → Architect | 直接传递用户构想 | 不使用 Brief 格式（仅 init/worldbuilding） |
| Orchestrator → Archivist | MigrationBrief | 批次章节列表 + 前批摘要 |
| Orchestrator → Architect（迁移合成） | ArchitectMigrationBrief | N 份 per-batch-extraction.yaml 路径列表 |

完整字段定义见 `runtime/handoff-schema.md`。
