# novel-studio — 小说智能运行时

面向中文长篇小说的 AI 写作 Agent 系统。

**核心理念**：用户只需表达意图（「写第10章」），系统自动编排 7 个 Agent 完成完整流水线——从章节规划、场景设计、正文起草到质量验收和状态更新，全程无需手动干预。

## 与旧版 novel-skills 的区别

| | novel-skills (v1) | novel-studio (v2) |
|---|---|---|
| 定位 | Skill 集合（工具箱） | Agent Runtime（操作系统） |
| 调用方式 | 用户手动依次调用各个 skill | 用户一个命令，自动流转全流程 |
| Agent/Skill 关系 | 混合在一起，边界模糊 | 严格分离：Agent=角色+决策，Skill=纯能力 |
| 大纲→正文 | 直接跨越，缺少中间层 | Scene Planner 做场景级节拍设计 |
| 品类支持 | 无品类区分 | 内置品类配方（番茄系统爽文），可扩展 |
| 状态管理 | 各 skill 各自修改 | State Manager 唯一写入口 |

## 架构总览

```
User
  │
  ▼
Orchestrator（入口 + 意图识别 + 多轮对话 + 调度）
  │
  ▼
Workflow Engine（状态机自动流转）
  │
  ├── Director ──→ Story Contract
  │       ▼
  ├── ScenePlanner ──→ Scene Contract
  │       ▼
  ├── Writer ──→ 正文 + 状态增量
  │       ▼
  ├── Critic ──→ Review Report（5 Checker）
  │       ▼
  └── StateManager ──→ 状态更新 + 记忆压缩
```

## 目录结构

```
novel-engine/
├── agents/              # 7 个 Agent 定义（角色 + 决策逻辑）
├── skills/              # 13 个纯能力 Skill（Agent 的工具箱）
│   ├── narrative/       # 对话/场景渲染/情绪兑现/视角控制
│   ├── analysis/        # AI味检测/信息泄漏/因果/节奏/人物/伏笔
│   └── craft/           # 文风校准/钩子设计/角色声音
├── workflows/           # 4 个 Workflow 状态机
├── commands/            # 5 个用户入口（slash command）
├── genres/              # 品类配方（番茄系统爽文 + 模板）
├── runtime/             # 状态 Schema + 上下文预算 + 记忆压缩协议
├── references/          # AI 味目录 + 失败案例库
├── DESIGN.md            # 完整架构设计文档
└── skills/              # [待清理] v1 旧版 skill 文件
```

## 快速开始

### 初始化项目

```
/novel init
```

系统会通过多轮对话确认品类、主角定位、篇幅和写作模式，然后自动创建工作区骨架。

### 写章节

```
/novel write 1
```

自动运行完整流水线：Director → ScenePlanner → Writer → Critic → StateManager。

### 修订章节

```
/novel revise 5
```

根据修订范围自动选择最优路径（全文重写/场景重设/局部修复/仅去味）。

### 质量检查

```
/novel check 5
```

只输出 Review Report，不修改正文。

### 世界观构建

```
/novel world
```

添加角色、完善力量体系、扩展世界观。

## 7 个 Agent

| Agent | 角色 | 所有权 |
|-------|------|--------|
| Orchestrator | 入口 + 意图识别 + 调度 | progress.yaml, agent-log.yaml |
| Architect | Canon 唯一所有者 | 00-书核/, 10-设定/ |
| Director | 故事状态 + 信息释放策略 | 20-大纲/ |
| ScenePlanner | 场景级节拍设计（五拍骨架） | 场景节拍 |
| Writer | 正文唯一执行者 | 30-正文/ |
| Critic | 5 Checker 质量门禁 | 验收标准 |
| StateManager | 状态更新 + 记忆压缩（唯一写入口） | 90-状态/ |

## 工作区结构（Agent 操作的目标）

```
my-novel/
├── 00-书核/作品总表.md
├── 10-设定/（硬设定 + 角色 + 世界观 + 力量体系）
├── 20-大纲/（全书总纲 + 分卷 + 伏笔账本）
├── 30-正文/（第X章.md）
├── 35-参考片段/
└── 90-状态/（author.yaml + reader.yaml + character.yaml + foreshadow.yaml + progress.yaml + agent-log.yaml）
```

## 许可证

Apache-2.0
