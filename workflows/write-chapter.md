---
type: workflow
name: write-chapter
description: "章节写作全流程。状态机自动流转 Director → ScenePlanner → Writer → Critic → StateManager。"
---

# write-chapter — 章节写作 Workflow

## 状态机

```
用户: /novel write <chapter>
            │
            ▼
    Orchestrator: 意图确认 + 多轮对话
            │
            ▼
    ┌──────────────────────────────────────────┐
    │         状态机自动流转                     │
    │                                           │
    │  NEED_PLAN                                │
    │    ↓ Director                             │
    │    ↓ 产出: Story Contract                  │
    │    ↓ 流转条件: Story Contract 已生成        │
    │                                           │
    │  NEED_SCENE                               │
    │    ↓ ScenePlanner                         │
    │    ↓ 产出: Scene Contract                  │
    │    ↓ 流转条件: Scene Contract 已生成        │
    │                                           │
    │  NEED_DRAFT                               │
    │    ↓ Writer                               │
    │    ↓ 产出: 正文 + state_delta              │
    │    ↓ 流转条件: 正文已生成 + 自检通过         │
    │                                           │
    │  NEED_REVIEW                              │
    │    ↓ Critic                               │
    │    ↓ 产出: Review Report                  │
    │    ↓                                      │
    │    ├── 通过 → StateManager → COMPLETED     │
    │    ├── 局部修复 → Writer(限制范围) → Critic │
    │    └── 骨架失效 → ScenePlanner(重设计)     │
    └──────────────────────────────────────────┘
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
INPUT: 用户指令 "/novel write 11"

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

```
INPUT: Orchestrator 交接包

DIRECTOR 动作:
  1. 加载必须上下文（Canon摘要/卷纲/4个状态文件）
  2. 加载品类配方 rhythm（如适用）
  3. 决策本章功能、信息释放策略、禁止触碰清单、旧线触碰
  4. 生成 Story Contract

ORCHESTRATOR 检查:
  - Story Contract 是否包含所有必填字段？
  - forbid_touch 是否有具体内容？
  - chapter_end_hook 是否可执行？

流转:
  - 通过 → 更新 progress.yaml: chapter_state = NEED_SCENE
  - 失败 → 回到 Director 重试 1 次

OUTPUT: Story Contract（YAML 格式）
```

### 步骤 3：Scene Planner 执行（NEED_SCENE）

```
INPUT: Story Contract + Orchestrator 交接包

SCENE PLANNER 动作:
  1. 加载 Story Contract
  2. 加载 POV 角色状态 + 最近 2 章正文结构
  3. 切分场景（每章 1-5 个场景）
  4. 每场景设计五拍骨架
  5. 分配视角、叙述距离、环境压力
  6. 检查场景间因果链
  7. 按品类配方配置爽点位置（如适用）
  8. 生成 Scene Contract

ORCHESTRATOR 检查:
  - 每场景是否都有可执行的五拍骨架？
  - 场景间是否有因果链（不是「然后」而是「因为所以」）？
  - 章尾落点是否与 Story Contract 对齐？

流转:
  - 通过 → 更新 progress.yaml: chapter_state = NEED_DRAFT
  - 失败 → 回到 ScenePlanner 重试 1 次

OUTPUT: Scene Contract（YAML 格式）
```

### 步骤 4：Writer 执行（NEED_DRAFT）

```
INPUT: Scene Contract + Orchestrator 交接包

WRITER 动作:
  1. 加载 Scene Contract
  2. 加载最近 2 章正文全文 + voice 样本
  3. 按场景顺序连续起草
  4. 每场景边界执行 4 项硬门禁
  5. 整章完成做 AI 味自检
  6. 生成正文 + state_delta

ORCHESTRATOR 检查:
  - 正文是否非空？
  - 硬门禁自检是否全部通过？
  - state_delta 是否完整？

流转:
  - 通过 → 更新 progress.yaml: chapter_state = NEED_REVIEW
  - 失败 → 回到 Writer 重试 1 次

OUTPUT: 正文文件 + state_delta（YAML 格式）
```

### 步骤 5：Critic 执行（NEED_REVIEW）

```
INPUT: 正文 + Scene Contract + Story Contract 约束

CRITIC 动作:
  1. Logic Checker（因果与连续性）
  2. Info Leak Checker（信息泄漏）
  3. Character Checker（人物一致性）
  4. Pace Checker（节奏）
  5. Style Checker（文风/AI味）
  6. 生成 Review Report

ORCHESTRATOR 检查:
  - 5 个 Checker 是否全部执行？
  - Review Report 判决是否明确？

流转:
  - 通过 → StateManager
  - 局部修复 → Writer（限制修改范围，只修标记项）→ 再回 Critic
  - 骨架失效 → ScenePlanner（重设计，不重跑 Director）

OUTPUT: Review Report（YAML 格式）
```

### 步骤 6：State Manager 执行（Critic 通过后）

```
INPUT: Review Report（通过）+ state_delta + 当前状态文件

STATE MANAGER 动作:
  1. 校验 Review Report.verdict == 通过
  2. 更新 author.yaml / reader.yaml / character.yaml / foreshadow.yaml
  3. 更新 progress.yaml（chapter+1, status=COMPLETED）
  4. 写入 agent-log
  5. 检查是否需要压缩（每5章/卷末/超50KB）

流转:
  - 完成 → Orchestrator 报告用户「第X章已完成」
  - 需要压缩 → 执行压缩后再报告

OUTPUT: 更新后的状态文件
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

```
读取 agent-log.yaml → 找到最后一条 in_progress 或 completed 记录
  ↓
如果最后一条是 'to_agent: Director, status: in_progress'
  → NEED_PLAN，重新调用 Director
如果最后一条是 'to_agent: Writer, status: in_progress'
  → NEED_DRAFT，重新调用 Writer
...
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
