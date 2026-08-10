# 流水线定义

> 本文档是 novel-studio 所有 Agent 流水线的**唯一权威定义**。
> 每个 Agent 在自己的文件中引用本文档，不自行描述流水线位置。

---

## 一、写章节（write-chapter）

**触发**: `/novel write <N>` | `/novel write next`

```mermaid
flowchart TD
    User["👤 User"]
    Orchestrator["🎯 Orchestrator<br/>意图确认 + 多轮对话<br/>读取 progress.yaml"]

    User --> Orchestrator

    subgraph StateMachine["状态机自动流转"]
        direction TB

        Director["📋 Director<br/><b>产出: Story Contract</b><br/>• 章节功能（推进/揭示/余震/过渡/高潮）<br/>• 信息释放策略<br/>• 旧线触碰计划"]

        ScenePlanner["🎬 ScenePlanner<br/><b>产出: Scene Contract</b><br/>• 每场景五拍骨架<br/>• 视角分配 + 叙述距离<br/>• 场景间因果链"]

        Writer["✍️ Writer<br/><b>产出: 正文 + state_delta</b><br/>• Scene Contract 约束内连续起草<br/>• 每场景硬门禁自检<br/>• 标记状态增量"]

        Critic["🔍 Critic<br/><b>产出: Review Report</b><br/>• Logic / Info Leak / Character<br/>• Pace / Style Checker"]

        StateManager["📋 StateManager<br/>更新全部状态文件"]
        Completed(["✅ COMPLETED<br/>报告用户"])
    end

    Orchestrator --> Director
    Director -->|"Story Contract ✓"| ScenePlanner
    ScenePlanner -->|"Scene Contract ✓"| Writer
    Writer -->|"正文 ✓ + 自检 ✓"| Critic
    Critic -->|"🟢 通过"| StateManager
    StateManager --> Completed

    Critic -->|"🟡 局部修复"| Writer
    Critic -->|"🔴 骨架失效"| ScenePlanner
```

**状态枚举**: NEED_PLAN → NEED_SCENE → NEED_DRAFT → NEED_REVIEW → COMPLETED

**交接包流转**:
| 步骤 | 交接包 |
|------|--------|
| Orchestrator → Director | DirectorBrief |
| Orchestrator → ScenePlanner | ScenePlannerBrief |
| Orchestrator → Writer | WriterBrief |
| Orchestrator → Critic | CriticBrief |
| Critic 通过 → StateManager | StateManagerBrief |

---

## 二、初始化项目（init-project）

**触发**: `/novel init`

```mermaid
flowchart TD
    User["👤 User: /novel init"]
    Orchestrator["🎯 Orchestrator<br/>多轮确认"]
    Architect["🏗️ Architect<br/><b>创建骨架</b><br/>• core/ + setting/<br/>• 按品类配方初始化设定<br/>• 生成硬设定 + 角色档案"]
    StateManager["📋 StateManager<br/><b>初始化状态</b><br/>• progress.yaml (chapter=0)<br/>• author / reader / character<br/>• foreshadow / agent-log"]
    Done(["✅ 项目就绪"])

    User --> Orchestrator
    Orchestrator -->|"品类/主角/篇幅/模式 已确认"| Architect
    Architect -->|"骨架创建完成"| StateManager
    StateManager --> Done
```

---

## 三、修订章节（revise-chapter）

**触发**: `/novel revise <N>`

```mermaid
flowchart TD
    User["👤 User: /novel revise N"]
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

**触发**: `/novel world`

```mermaid
flowchart TD
    User["👤 User: /novel world"]
    Orchestrator["🎯 Orchestrator<br/>确认构建范围"]
    Architect["🏗️ Architect<br/><b>创建/更新 canon</b><br/>• 新增角色档案<br/>• 扩展世界观/力量体系<br/>• 更新硬设定清单"]
    StateManager["📋 StateManager<br/>同步 character.yaml<br/>更新 agent-log"]
    Done(["✅ 报告用户"])

    User --> Orchestrator
    Orchestrator -->|"添加角色/补设定/修冲突"| Architect
    Architect -->|"canon 已更新"| StateManager
    StateManager --> Done
```

---

## 五、质量检查（novel-check）

**触发**: `/novel check <N>`

```mermaid
flowchart LR
    User["👤 User: /novel check N"]
    Orchestrator["🎯 Orchestrator<br/>加载章节路径"]
    Critic["🔍 Critic<br/><b>5 Checker 只读扫描</b><br/>• 产出 Review Report<br/>• 不触发修复<br/>• 不更新状态"]
    Done(["📊 仅报告，不修改任何文件"])

    User --> Orchestrator
    Orchestrator --> Critic
    Critic --> Done
```

---

## 六、项目迁移（migrate-project）

**触发**: `/novel migrate <现有目录路径>`

```mermaid
flowchart TD
    User["👤 User: /novel migrate path"]
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

    ArchivistN -->|"N份提取结果"| Architect["🏗️ Architect<br/><b>合成归档</b><br/>• 角色去重合并<br/>• 伏笔候选升级<br/>• 硬设定合并<br/>• 品类确认<br/>→ migration-extraction.yaml"]

    Architect -->|"提取结果"| OrchestratorConfirm["🎯 Orchestrator<br/><b>多轮作者确认</b><br/>• 角色确认+补充<br/>• 伏笔确认<br/>• 秘密收集<br/>• 大纲导入"]

    OrchestratorConfirm -->|"确认完毕"| ArchGen["🏗️ Architect<br/>写入 setting/ 全部文件"]
    OrchestratorConfirm -->|"确认完毕"| StateGen["📋 StateManager<br/>写入 state/ 全部文件"]

    ArchGen --> Done(["✅ 迁移完成<br/>后续可使用 /novel write"])
    StateGen --> Done
```

详见 [`workflows/migrate-project.md`](migrate-project.md)。

---

## Agent ↔ 流水线对应关系

| Agent | 出现在流水线 |
|-------|-------------|
| Orchestrator | 全部六条 |
| Architect | 初始化、世界观构建、项目迁移（合成归档） |
| Archivist | 项目迁移（分批分析）——迁移完成后不再使用 |
| Director | 写章节（修订-全文重写） |
| ScenePlanner | 写章节、修订（全文重写/场景重设） |
| Writer | 写章节、修订（全部四种范围） |
| Critic | 写章节、修订（全部四种范围）、质量检查 |
| StateManager | 写章节、初始化、修订、世界观构建、项目迁移（文件生成） |

---

## 关键约束

1. **Agent 不自选后继**: 下一步由状态机决定，不由 Agent 推荐
2. **Orchestrator 是唯一中转站**: Agent 之间不直接通信，所有信息经 Orchestrator 传递
3. **StateManager 是唯一写入口**: 其他 Agent 只标记增量，不直接写 `state/` 文件
4. **Writer 不读大纲**: 渐进披露，Writer 只知道 Scene Contract 和禁止触碰清单
5. **交接包裁剪**: Orchestrator 按 `runtime/handoff-schema.md` 裁剪交接包，下游 Agent 只收到所需字段

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
