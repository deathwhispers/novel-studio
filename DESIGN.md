# novel-studio: 小说智能运行时 — 架构设计

## 一、背景与目标

将 `novel-skills` 从「Skill 集合」彻底重构为 **Novel Agent Runtime（小说智能运行时）**。

核心目标：
1. **用户只需表达意图**，系统自动完成 Agent 编排（不再手动依次调用）
2. **Agent / Skill / Workflow 三者严格分离**
3. **填补大纲→正文之间的 Scene Planner**，解决正文质量瓶颈
4. **内置番茄系统爽文品类配方**，Writer 保留灵活调整自由度
5. **State Manager 作为状态唯一写入口**，确保长期一致性

---

## 二、核心概念定义

### Agent（角色 + 决策权）
- 有明确的**所有权**（哪些文件归它管）
- 有**决策权**（决定何时使用哪个 Skill）
- 有**上下文预算**（严格 token 上限）
- 不直接调用其他 Agent（通过 Workflow 引擎流转）

### Skill（纯能力，零决策）
- 被 Agent 调用，不自发运行
- 只描述「怎么做」，不描述「什么时候做」
- 无状态、无上下文预算（预算由调用方 Agent 控制）

### Workflow（状态机，自动流转）
- 定义 Agent 的执行顺序和流转条件
- 状态决定下一步，Agent 不自选后继
- 用户触发入口，后续全自动

---

## 三、目录结构

```
novel-studio/
│
├── agents/                        # Agent 定义（角色 + 决策逻辑）
│   ├── orchestrator.md            # 入口 + 意图识别 + 多轮对话 + 流程调度
│   ├── architect.md               # Canon 唯一所有者（世界观 + 立项）
│   ├── director.md                # 故事状态 + 信息释放策略
│   ├── scene-planner.md           # 场景级节拍设计（五拍骨架）
│   ├── writer.md                  # 正文唯一执行者
│   ├── critic.md                  # 5 Checker 质量门禁
│   └── state-manager.md           # 状态更新 + 记忆压缩（唯一写入口）
│
├── commands/                      # 用户入口（slash command）
│   ├── novel-init.md
│   ├── novel-write.md
│   ├── novel-revise.md
│   ├── novel-check.md
│   └── novel-world.md
│
├── skills/                        # 纯能力库（Agent 的工具箱）
│   ├── narrative/                 # 叙事能力
│   │   ├── dialogue.md
│   │   ├── scene-render.md
│   │   ├── emotion-payoff.md
│   │   └── pov-control.md
│   ├── analysis/                  # 分析能力
│   │   ├── ai-flavor-detect.md
│   │   ├── info-leak-check.md
│   │   ├── causality-check.md
│   │   ├── pacing-check.md
│   │   ├── character-check.md
│   │   └── foreshadow-check.md
│   └── craft/                     # 手艺能力
│       ├── style-calibrate.md
│       ├── hook-design.md
│       └── voice-check.md
│
├── workflows/                     # 状态机定义
│   ├── write-chapter.md           # 写章节全流程
│   ├── revise-chapter.md          # 修订章节流程
│   ├── init-project.md            # 初始化项目流程
│   └── worldbuilding.md           # 世界观构建流程
│
├── genres/                        # 品类配方
│   ├── 番茄系统爽文/
│   │   ├── recipe.md              # 核心公式：任务→奖励→打脸→升级 循环
│   │   ├── rhythm.md              # 章节节奏模板（爽点密度/打脸频率/升级间隔）
│   │   ├── tropes.md              # 常见变体（签到流/抽奖流/任务流/神豪流）
│   │   └── examples.md            # 爆款拆解范例
│   └── _template/                 # 新品类模板
│
├── runtime/                       # 运行时规范
│   ├── state-schema.md            # 所有状态文件的 YAML schema
│   ├── context-budget.md          # 各 Agent 的 token 预算表
│   └── memory-compress.md         # 记忆压缩协议
│
├── references/                    # 共享参考资料
│   ├── failure-cases.md           # 50 失败模式
│   ├── ai-flavor-catalog.md       # AI 味检测目录
│   └── writing-glossary.md        # 写作术语表
│
├── install.sh                     # 全局安装脚本
├── DESIGN.md
└── README.md
```

---

## 四、用户工作区结构（运行时生成）

Agent 操作的工作区，与 `novel-studio` 本身分离：

```
my-novel/
├── core/
│   └── 作品总表.md
├── setting/
│   ├── 硬设定.yaml
│   ├── characters/
│   ├── world/
│   └── power-system/
├── outline/
│   ├── 全书总纲.md
│   ├── volumes/
├── chapters/
│   └── 第X章-章节名.md
├── snippets/                   # 用户自填的段落素材
└── state/                       # 运行时状态（Agent 读写）
    ├── author.yaml                # 作者已知的秘密/计划
    ├── reader.yaml                # 读者已知/猜测的状态
    ├── character.yaml             # 各 POV 角色的认知状态
    ├── foreshadow.yaml            # 伏笔追踪（活跃/已揭示/已回收）
    ├── progress.yaml              # 当前进度 + 工作区文件索引
    └── agent-log.yaml             # Agent 运行日志（断点恢复用）
```

---

## 五、7 Agent 定义

### 1. Orchestrator（入口 + 调度）

| 属性 | 值 |
|------|-----|
| 所有权 | `state/progress.yaml`、`state/agent-log.yaml` |
| 上下文预算 | ~2K tokens |
| 加载 | progress.yaml + agent-log.yaml |
| 绝不加载 | 正文/大纲/设定/canon |

**核心职责**：
- 接收用户指令，进行**多轮对话**澄清意图（不假设、不跳过）
- 读取 progress.yaml，判断当前状态
- 按 Workflow 状态机自动调度下游 Agent
- Agent 返回后检查输出，写入 agent-log，决定继续流转或暂停
- 本身不做任何创作、检查或状态修改

**多轮对话规则**：
- 用户说「写第10章」→ 先确认本章的核心冲突/爽点方向（1-2个问题）
- 用户说「开新书」→ 先确认品类/题材/主角定位/篇幅（3-5个问题）
- 用户已给出完整方案时走快速通道
- 每轮最多 3 个关键问题，已有上下文可判断的直接标注

### 2. Architect（Canon 所有者）

| 属性 | 值 |
|------|-----|
| 所有权 | `core/`、`setting/` |
| 上下文预算 | ~8K tokens |
| 加载 | 用户构想 + 已有 canon + 品类配方（如适用） |
| 绝不加载 | 正文/大纲/状态文件 |

**核心职责**：
- 创建/更新世界规则、人物设定、力量体系、时间线
- 维护「硬设定清单」——下游任何 Agent 不可违反
- 新项目时读取品类配方（如番茄系统爽文），按品类特征初始化设定骨架
- 回答下游 Agent 的 canon 查询（通过 Orchestrator 中转）

### 3. Story Director（故事状态所有者）

| 属性 | 值 |
|------|-----|
| 所有权 | `outline/` |
| 上下文预算 | ~6K tokens |
| 加载 | Canon 摘要 + 当前卷纲 + author.yaml + reader.yaml + character.yaml + foreshadow.yaml |
| 绝不加载 | 完整正文 |

**核心职责**：
- 决定本章功能（推进/揭示/余震/过渡/高潮）
- 从 author.yaml 提取本章**禁止触碰清单**
- 从 foreshadow.yaml 选择 0-2 条需要轻碰的旧线
- 规划信息释放节奏
- 输出 **Story Contract**（章节功能 + 信息释放策略 + 禁止触碰清单 + 旧线计划）
- 品类配方可用时，参照品类节奏模板调整推进密度

### 4. Scene Planner（场景执行设计师）

| 属性 | 值 |
|------|-----|
| 所有权 | 场景节拍设计 |
| 上下文预算 | ~4K tokens |
| 加载 | Story Contract + POV 角色状态 + 最近 2 章正文结构 |
| 绝不加载 | 完整大纲/完整 canon |

**核心职责**：
- 将 Story Director 的「本章功能」翻译为**每场景五拍骨架**（目标→阻碍→变化→意外→新问题）
- 确定主视角、叙述距离、场景空间和环境压力
- 设计冲突推进方式（对抗/误读/隐瞒/试探/环境压力）
- 衔接场景间因果链
- 输出 **Scene Contract**（五拍骨架 + 视角约束 + 场景氛围 + 章尾落点）
- 品类配方可用时，按品类节奏模板配置爽点间隔和场景类型轮换

### 5. Writer（正文执行者）

| 属性 | 值 |
|------|-----|
| 所有权 | `chapters/` |
| 上下文预算 | ~6K tokens |
| 加载 | Scene Contract + 最近 2 章正文 + voice 样本 + 1-2 参考片段 |
| 绝不加载 | 完整大纲/完整 canon/状态文件 |

**核心职责**：
- 在 Scene Contract 约束内连续起草
- **不知道第 50 章的反转**，只知道「本章可以释放 Y、禁止触碰 X」
- 每个场景边界执行硬门禁（视角跳转？违反动机？撞硬设定？因果断裂？）
- 调用 narrative skills（dialogue/scene-render/emotion-payoff/pov-control）
- 品类配方可用时，调用品类 tropes 参考但保留灵活调整权
- 输出正文 + **状态增量标记**（本章实际发生的变化）

### 6. Critic（质量门禁）

| 属性 | 值 |
|------|-----|
| 所有权 | 验收标准 |
| 上下文预算 | ~5K tokens |
| 加载 | 正文 + Scene Contract + Story Contract 约束 + AI 味目录 |
| 绝不加载 | 完整 canon/完整大纲/其他章节 |

**5 个 Checker（按序执行）**：
1. **Logic Checker**：因果链、连续性、硬设定违反
2. **Info Leak Checker**：正文是否触碰禁止触碰清单
3. **Character Checker**：人物动机、选择可信度、POV 认知边界
4. **Pace Checker**：场景节拍执行、节奏断裂
5. **Style Checker**：AI 味扫描、角色辨识度、voice 漂移

**输出 Review Report**：通过 / 局部修复 / 骨架失效

### 7. State Manager（状态唯一写入口）

| 属性 | 值 |
|------|-----|
| 所有权 | `state/`（所有状态文件） |
| 上下文预算 | ~3K tokens |
| 加载 | Review Report + 正文状态增量标记 + 当前状态文件 |
| 绝不加载 | 正文/大纲/canon |

**核心职责**：
- Critic 通过后才执行更新
- 更新 author.yaml（新秘密/已揭示归档）
- 更新 character.yaml（各 POV 角色已知/不知/误判）
- 更新 reader.yaml（读者已知/猜测方向）
- 更新 foreshadow.yaml（新线索/已回收）
- 每 5 章执行**记忆压缩**
- **不判断质量、不修改正文、不决定剧情方向**

---

## 六、Workflow 状态机

### write-chapter（核心流程）

```
用户: /novel write 10
        │
        ▼
Orchestrator: 识别意图 → 多轮确认 → 读取 progress.yaml
        │
        ▼
┌─────────────────────────────────────────────┐
│  状态机自动流转（Agent 不自选后继）            │
│                                              │
│  NEED_PLAN ──→ Director ──→ Story Contract   │
│       │                                      │
│       ▼                                      │
│  NEED_SCENE ──→ ScenePlanner ──→ Scene Contract │
│       │                                      │
│       ▼                                      │
│  NEED_DRAFT ──→ Writer ──→ 正文 + 增量标记    │
│       │                                      │
│       ▼                                      │
│  NEED_REVIEW ──→ Critic ──→ Review Report     │
│       │                                      │
│       ├── 通过 ──→ StateManager ──→ COMPLETED │
│       ├── 局部修复 ──→ Writer(修复) ──→ Critic │
│       └── 骨架失效 ──→ ScenePlanner(重设计)    │
└─────────────────────────────────────────────┘
```

状态枚举：
- `NEED_PLAN`：缺少本章 Story Contract → 调用 Director
- `NEED_SCENE`：缺少 Scene Contract → 调用 Scene Planner
- `NEED_DRAFT`：缺少正文 → 调用 Writer
- `NEED_REVIEW`：正文已有但未验收 → 调用 Critic
- `COMPLETED`：验收通过 + 状态已更新

**流转规则**：
- 状态决定下一步，永远不靠 Agent 自己选
- Critic 返回「局部修复」→ 回到 Writer，但限制修改范围
- Critic 返回「骨架失效」→ 回到 Scene Planner，不重跑 Director
- 任何 Agent 异常 → Orchestrator 记录日志，暂停并报告用户

### init-project

```
用户: /novel init
        │
        ▼
Orchestrator: 多轮确认（品类/题材/主角/篇幅）
        │
        ▼
Architect: 创建 core/ + setting/ 骨架
        │
        ▼
（品类配方可选）Architect 按 genre recipe 初始化设定模板
        │
        ▼
StateManager: 初始化 progress.yaml
        │
        ▼
COMPLETED
```

### revise-chapter

```
用户: /novel revise 10
        │
        ▼
Orchestrator: 确认修订范围（全文重写/局部修复/仅去味）
        │
        ▼
Director → ScenePlanner → Writer → Critic → StateManager
（根据修订范围可能跳过 Director/ScenePlanner）
```

---

## 七、品类配方设计（番茄系统爽文）

### recipe.md 核心结构

```yaml
品类: 番茄系统爽文
目标平台: 番茄小说
核心读者预期:
  - 每章至少一个爽点兑现
  - 主角快速成长（不能压级超过10章）
  - 打脸要有见证者（读者代入的爽感来源）
  - 系统是主角的核心优势，不能长期失效

核心循环:
  触发 → 任务下达 → 阻力出现 → 主角破局 → 奖励兑现 → 打脸/震惊 → 新任务暗示

章节节奏基线:
  章首钩子(500字) → 加压/冲突(1500字) → 爽点兑现(300字) → 章尾新钩子(200字)

爽点类型权重:
  - 能力兑现: 35%
  - 认知翻转（打脸）: 30%
  - 资源获取: 20%
  - 关系支援: 10%
  - 公道回收: 5%

升级节奏:
  - 小升级（技能/资源）: 每3-5章
  - 中升级（段位/身份）: 每10-15章
  - 大升级（世界观层级）: 每卷1-2次

禁忌:
  - 主角连续3章无主动行为
  - 系统连续5章不出场
  - 反派智商突然下降来成全主角
  - 奖励无代价（每次获得必须有付出）
```

### Agent 如何使用品类配方

- **Architect**：初始化时参考 recipe 构建力量体系和角色骨架
- **Director**：参考 rhythm 设计章节功能和推进密度
- **Scene Planner**：参考爽点权重分配场景类型
- **Writer**：参考 tropes 但不机械套用，保留灵活调整权
- **Critic**：参考禁忌列表做品类专项检查

---

## 八、Skill 调用协议

Agent 调用 Skill 的规范：

```text
【Skill 调用 — Writer → dialogue.md】

场景上下文：{{当前场景的冲突状态和角色关系}}
执行约束：{{Scene Contract 中的相关约束}}
输出要求：{{具体需要产出的内容}}

Skill 返回后，Writer 判断是否采纳、修改或弃用。
Skill 不感知 Agent 状态，不感知 Workflow 阶段。
```

关键规则：
- Skill 只产出内容建议，不修改 Agent 的状态文件
- Agent 对 Skill 产出有最终决定权
- 同一个 Skill 可被多个 Agent 调用（如 ai-flavor-detect 可被 Writer 写中自检和 Critic 正式扫描同时使用）

---

## 九、交接包格式（Agent → Agent）

```yaml
handoff:
  from: Director
  to: Scene Planner
  chapter: 10
  mode: 商业连载

  # 上游核心输出
  contract:
    chapter_function: 推进（主角首次使用新能力）
    info_release:
      can_reveal: [能力名称, 能力效果]
      can_hint: [能力代价]
      forbid_touch: [能力来源真相, 系统隐藏规则]
    thread_touch: [第3章埋的玉佩线索]
    chapter_end_hook: "主角用新能力解决了眼前危机，但系统弹出了意想不到的新任务"

  # 变化增量（下游最关心的不是历史，是变化）
  decision_delta:
    reader_suspicion:
      主角能力来源: +15%
    character_pressure:
      主角: +20 (新能力的代价开始显现)
    open_questions:
      - 系统为什么在这个时机发布这个任务？

  # 下游启动指令
  downstream:
    must_read:
      - outline/volumes/volume-01.md
      - state/character.yaml
    must_not_read:
      - 完整正文
      - 后续章节大纲
    budget: 4K tokens
```

---

## 十、实施计划

### Phase 1：骨架搭建
1. 创建全部子目录（agents/skills/workflows/commands/genres/runtime/references）
2. 编写 `runtime/state-schema.md`（所有状态文件 YAML schema）
3. 编写 `runtime/context-budget.md`（Agent token 预算表）
4. 编写 `runtime/memory-compress.md`（记忆压缩协议）

### Phase 2：Agent 定义
5. 编写 7 个 Agent 定义文件（orchestrator/architect/director/scene-planner/writer/critic/state-manager）
6. 每个 Agent 明确：角色、所有权、上下文预算、加载清单、绝不加载清单、决策规则

### Phase 3：Workflow 定义
7. 编写 `workflows/write-chapter.md`（核心状态机）
8. 编写 `workflows/init-project.md`
9. 编写 `workflows/revise-chapter.md`
10. 编写 `workflows/worldbuilding.md`

### Phase 4：Skill 迁移 + 精简
11. 从旧 `novel-skills` 提取 AI 味目录 → `references/ai-flavor-catalog.md`
12. 从旧项目提取 50 失败模式 → `references/failure-cases.md`
13. 将旧项目写作技法拆分为纯能力 skill（narrative/analysis/craft 三个目录，约 13 个 skill）
14. 每个 skill 移除角色决策逻辑，只保留「怎么做」的纯能力描述

### Phase 5：品类配方
15. 编写 `genres/番茄系统爽文/recipe.md`
16. 编写 `genres/番茄系统爽文/rhythm.md`
17. 编写 `genres/番茄系统爽文/tropes.md`
18. 编写 `genres/番茄系统爽文/examples.md`
19. 编写 `genres/_template/` 新品类模板

### Phase 6：Command 入口
20. 编写 `commands/novel-init.md`
21. 编写 `commands/novel-write.md`
22. 编写 `commands/novel-revise.md`
23. 编写 `commands/novel-check.md`
24. 编写 `commands/novel-world.md`

### Phase 7：验证 + 清理
25. 用空白工作区跑通 `novel init` → `novel write 1` 完整流程
26. 连续写 3 章验证状态递延正确性
27. 更新 README

---

## 十一、关键设计决策

1. **Agent 不直接通信**：所有跨 Agent 信息通过 Orchestrator 中转 + 状态文件共享
2. **Writer 不读大纲**：渐进披露是防上帝视角的核心机制
3. **State Manager 是唯一写入口**：其他 Agent 只标记增量，不直接写状态文件
4. **品类配方是参考而非模板**：Writer 始终保有灵活调整权，品类配方只降低默认决策成本
5. **多轮对话在 Orchestrator 层完成**：下游 Agent 收到的是已确认的意图，不再反问用户
6. **状态机固定**：Agent 不自选后继，消除「Agent 应该找谁」的不确定性

---

## 十二、验证方式

1. 初始化空工作区 → `/novel init` → 选择番茄系统爽文 → 确认生成完整目录骨架
2. `/novel write 1` → 自动流转 Director → ScenePlanner → Writer → Critic → StateManager，中间不需要用户干预
3. 连续 `/novel write 2` `/novel write 3` → 检查 character.yaml 和 foreshadow.yaml 是否正确递延
4. Writer 输出的正文中搜索 AI 味关键词（仿佛/似乎/感到/随着/在这一刻）→ Critic 能检测并阻止
5. Writer 输出的正文中搜索禁止触碰清单中的内容 → Info Leak Checker 能检测
