---
type: workflow
name: write-chapter
description: "章节写作全流程。状态机自动流转 Director → ScenePlanner → Writer → Critic → StateManager。"
---

# write-chapter — 章节写作 Workflow

## 状态机

```mermaid
flowchart TD
    User["👤 User: /novel-studio:write N"]
    Orchestrator["🎯 Orchestrator<br/>意图确认 + 多轮对话"]

    User --> Orchestrator

    subgraph AutoFlow["状态机自动流转"]
        direction TB

        NEED_PLAN["🔵 NEED_PLAN"]
        Director["📋 Director<br/>产出: Story Contract"]
        NEED_SCENE["🔵 NEED_SCENE"]
        ScenePlanner["🎬 ScenePlanner<br/>产出: Scene Contract"]
        NEED_DRAFT["🔵 NEED_DRAFT"]
        Writer["✍️ Writer<br/>产出: 正文 + state_delta"]
        NEED_REVIEW["🔵 NEED_REVIEW"]
        Critic["🔍 Critic<br/>产出: Review Report"]
        StateManager["📋 StateManager"]
        Completed(["✅ COMPLETED"])

        NEED_PLAN --> Director
        Director -->|"Story Contract ✓"| NEED_SCENE
        NEED_SCENE --> ScenePlanner
        ScenePlanner -->|"Scene Contract ✓"| NEED_DRAFT
        NEED_DRAFT --> Writer
        Writer -->|"正文 ✓ + 自检 ✓"| NEED_REVIEW
        NEED_REVIEW --> Critic
        Critic -->|"🟢 通过"| StateManager
        StateManager --> Completed
        Critic -->|"🟡 局部修复"| Writer
        Critic -->|"🔴 骨架失效"| ScenePlanner
    end

    Orchestrator --> NEED_PLAN
```

## 状态定义

| 状态 | 含义 | 触发条件 | 下一个 Agent |
|------|------|---------|-------------|
| NEED_PLAN | 缺少本章 Story Contract | progress.yaml chapter_state.status == NEED_PLAN | Director |
| NEED_SCENE | 缺少 Scene Contract | progress.yaml chapter_state.status == NEED_SCENE | ScenePlanner |
| NEED_DRAFT | 缺少正文 | progress.yaml chapter_state.status == NEED_DRAFT | Writer |
| NEED_REVIEW | 正文已有未验收 | progress.yaml chapter_state.status == NEED_REVIEW | Critic |
| COMPLETED | 验收通过+状态已更新 | progress.yaml chapter_state.status == COMPLETED | — |

## 详细流转步骤

### 步骤 1：Orchestrator 入口

```
INPUT: 用户指令 "/novel-studio:write 11"

ORCHESTRATOR 动作:
  1. 读取 progress.yaml
  2. 如果 chapter_state 已有状态（断点恢复）→ 从该状态继续
  3. 如果是新章节:
     - 计算下一章号（current.chapter + 1）
     - 多轮确认本章方向（1-2个问题）
     - 写入 progress.yaml: chapter_state = NEED_PLAN
  4. 生成交接包 → 传递给 Director
```

### 步骤 2：Director 执行（NEED_PLAN）

```mermaid
flowchart LR
    Input["📥 INPUT<br/>DirectorBrief 交接包"]
    Director["📋 Director<br/>• 加载状态摘要<br/>• 加载卷纲 + 品类配方<br/>• 决策章节功能 + 信息释放<br/>• 生成 Story Contract"]
    Check{"Orchestrator 检查<br/>必填字段完整?"}
    Pass["流转: NEED_SCENE"]
    Fail["重试 1 次<br/>仍失败 → 暂停"]
    Output["📤 OUTPUT<br/>Story Contract"]

    Input --> Director
    Director --> Output
    Output --> Check
    Check -->|"✓"| Pass
    Check -->|"✗"| Fail
```

### 步骤 3：Scene Planner 执行（NEED_SCENE）

```mermaid
flowchart LR
    Input["📥 INPUT<br/>ScenePlannerBrief<br/>（Story Contract + 结构）"]
    SP["🎬 ScenePlanner<br/>• 切分场景（1-5个）<br/>• 每场景五拍骨架<br/>• 分配视角/叙述距离<br/>• 检查场景间因果链<br/>• 配置爽点位置"]
    Check{"Orchestrator 检查<br/>五拍可执行?<br/>因果链完整?"}
    Pass["流转: NEED_DRAFT"]
    Fail["重试 1 次<br/>仍失败 → 暂停"]
    Output["📤 OUTPUT<br/>Scene Contract"]

    Input --> SP
    SP --> Output
    Output --> Check
    Check -->|"✓"| Pass
    Check -->|"✗"| Fail
```

### 步骤 4：Writer 执行（NEED_DRAFT）

```mermaid
flowchart LR
    Input["📥 INPUT<br/>WriterBrief<br/>（scenes + 约束 + 章尾）"]
    Writer["✍️ Writer<br/>• 读取最近2章正文 + voice 样本<br/>• 按场景顺序连续起草<br/>• 每场景边界硬门禁自检<br/>• AI 味自检<br/>• 生成 state_delta"]
    Check{"Orchestrator 检查<br/>正文非空?<br/>硬门禁全部通过?"}
    Pass["流转: NEED_REVIEW"]
    Fail["重试 1 次<br/>仍失败 → 暂停"]
    Output["📤 OUTPUT<br/>正文 + state_delta"]

    Input --> Writer
    Writer --> Output
    Output --> Check
    Check -->|"✓"| Pass
    Check -->|"✗"| Fail
```

### 步骤 5：Critic 执行（NEED_REVIEW）

```mermaid
flowchart LR
    Input["📥 INPUT<br/>CriticBrief<br/>（合并检查清单 + 正文路径）"]
    Critic["🔍 Critic<br/>• 1. Logic Checker<br/>• 2. Info Leak Checker<br/>• 3. Character Checker<br/>• 4. Pace Checker<br/>• 5. Style Checker<br/>• 生成 Review Report"]
    Check{"判决?"}
    Pass["🟢 通过 → StateManager"]
    LocalFix["🟡 局部修复 → Writer → 再回 Critic"]
    StructureFail["🔴 骨架失效 → ScenePlanner"]
    Output["📤 OUTPUT<br/>Review Report"]

    Input --> Critic
    Critic --> Output
    Output --> Check
    Check -->|"5 Checker 全过"| Pass
    Check -->|"硬伤 / >3个问题"| LocalFix
    Check -->|"骨架级问题"| StructureFail
```

### 步骤 6：State Manager 执行（Critic 通过后）

```mermaid
flowchart TD
    Input["📥 INPUT<br/>StateManagerBrief<br/>（Review Report + state_delta）"]
    Validate{"校验<br/>Review Report.verdict<br/>== 通过?"}
    Reject["⛔ 拒绝执行<br/>状态不更新"]
    Load["读取 4 个状态文件"]
    Update["逐项更新<br/>• author.yaml<br/>• reader.yaml<br/>• character.yaml<br/>• foreshadow.yaml<br/>• progress.yaml<br/>• agent-log"]
    Compress{"需要压缩?<br/>每5章 / 卷末 / >50KB"}
    ExecCompress["执行压缩协议"]
    Done["📤 OUTPUT<br/>更新后的状态文件<br/>→ Orchestrator 报告用户"]

    Input --> Validate
    Validate -->|"✗ 未通过"| Reject
    Validate -->|"✓ 通过"| Load
    Load --> Update
    Update --> Compress
    Compress -->|"是"| ExecCompress
    Compress -->|"否"| Done
    ExecCompress --> Done
```

## 错误处理矩阵

| 失败位置 | 错误类型 | 处理 |
|---------|---------|------|
| Director | Story Contract 不完整 | 重试 1 次，仍失败暂停并报告用户 |
| ScenePlanner | 五拍骨架不可执行 | 重试 1 次，仍失败暂停并报告用户 |
| Writer | 硬门禁未通过 | 回 Writer 修复（不重跑 Director/ScenePlanner） |
| Writer | 卡文无法继续 | 暂停并报告用户 |
| Critic | 局部修复 | 回 Writer（限制修改范围），修完再回 Critic |
| Critic | 骨架失效 | 回 ScenePlanner（重设计），不重跑 Director |
| Critic | 大面积信息泄漏 | 回 Director（重新设计信息释放策略） |
| StateManager | 状态更新失败 | 重试 1 次，仍失败保留 state_delta 待手动处理 |

## 断点恢复

当 Orchestrator 启动时检测到 `chapter_state.status` 不是 COMPLETED：

```mermaid
flowchart TD
    Start["读取 agent-log.yaml 最后一条"]
    Check{"最后一条状态?"}
    InProgress["status: in_progress"]
    Completed2["status: completed"]

    Resume{"从哪个 Agent 继续?"}

    Resume_Director["NEED_PLAN<br/>→ 重新调用 Director"]
    Resume_ScenePlanner["NEED_SCENE<br/>→ 重新调用 ScenePlanner"]
    Resume_Writer["NEED_DRAFT<br/>→ 重新调用 Writer"]
    Resume_Critic["NEED_REVIEW<br/>→ 重新调用 Critic"]
    Verify["检查 progress.yaml<br/>确认状态一致性"]
    Fresh["从头开始意图识别<br/>（agent-log 不存在）"]

    Start --> Check
    Check -->|"有 in_progress"| InProgress
    Check -->|"最后一条 completed"| Completed2
    Check -->|"不存在"| Fresh
    InProgress --> Resume
    Resume -->|"to_agent: Director"| Resume_Director
    Resume -->|"to_agent: ScenePlanner"| Resume_ScenePlanner
    Resume -->|"to_agent: Writer"| Resume_Writer
    Resume -->|"to_agent: Critic"| Resume_Critic
    Completed2 --> Verify
```

## 用户可见的输出

Orchestrator 在每一步向用户报告进度（不暴露 Agent 名）：

```
✍️ 正在规划第11章的故事方向…
✅ 章节方向已确定（推进：主角首次使用新能力）

🎬 正在设计场景结构…
✅ 3 个场景已编排完成

📝 正在写作中…
✅ 第11章完成（2500字）

🔍 正在质量检查…
✅ 检查通过（AI味 2处已自动修复，无硬伤）

📋 状态已更新 → 第11章完结
```
