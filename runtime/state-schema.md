# 状态文件 Schema

> 定义工作区 `state/` 下所有 YAML 文件的结构和字段约束。State Manager 是本文件定义的唯一实现者。

---

## 一、progress.yaml

工作区当前进度索引。

```yaml
# progress.yaml
schema_version: 3             # 结构版本号，见「七、文件版本与兼容」。缺失或 <3 → 触发 upgrade 流程
state_version: 15             # 事务版本号（整数递增），StateManager 每次状态更新 +1。缺失视为 1，首次更新时补齐。见「八」
workspace:
  name: "作品名称"
  genre: "番茄系统爽文"         # 品类标识，关联 genres/ 下的配方
  mode: "商业连载"              # 商业连载 | 类型长篇 | 文学叙事 | 短篇 | 探索起草
  created: "2026-01-01"
  chapter_word_target: 2000     # 每章目标字数（默认 2000，浮动 ±20%），由 Orchestrator 提取进 WriterBrief

current:
  chapter: 10                   # 当前已完成的最后一章编号
  volume: 1                     # 当前卷号
  total_chapters_written: 10
  total_words: 25000
  last_updated: "2026-01-15T10:30:00"

chapter_state:                  # 当前正在写的章节状态
  chapter_number: 11
  status: "WRITING"             # DIRECTION（方向确认中）| WRITING（逐段写作中）| COMPLETED（已锁定）
  chapter_direction: ""         # 本章方向（一句话）
  draft: ""                     # 正文文件路径
  segment_count: 0              # 已写成段数

# ===== chunk 块（节拍批量确认 Loop 的运行时进度）=====
# 详见第十节「chunk 字段定义与生命周期」。
chunk_plan:
  current_chunk: null           # 当前活跃 chunk id（null = 未启动 chunk）
  source: null                  # chunk 设计文件路径（outline/chunks/chunk-XX.yaml）
  current_beat: null            # 当前正在处理的 beat id（null = chunk 全部完成）
  chapter_range: null           # 本 chunk 覆盖的章节号 [start, end]
  chapter_word_target: null     # 继承自 workspace.chapter_word_target，可被 chunk 级覆盖
  confirmed_beats: {}           # 节拍确认状态，key=beat_id；详见第十节 1.3 节
  loop_state: null              # LOOP | WRITING | REVIEW | LOCKED
  loop_iteration: 0             # LOOP 重入次数（含首次进入）
  loop_entered_at: null         # 进入当前 LOOP 状态的时间
  beats_written: 0              # 当前章节已写完的 beat 数
  beats_total: 0                # 当前章节的 beat 总数（非 chunk 全部）
  words_written: 0              # 当前章节已写累计字数
  writing_started_at: null      # 当前章节写作开始时间
  loop_revert_log: []           # LOOP 回退日志（详见第十节 3.6 节）

files:
  book_core: "core/作品核心.md"
  hard_rules: "setting/硬规则.yaml"
  outline: "outline/全书总纲.yaml"
  volumes:
    - "outline/volumes/volume-01.yaml"
  chunks_dir: "outline/chunks/"
  chapters_dir: "chapters/"

next_milestone:
  type: "卷末"                  # 卷末 | 中段审视 | 完本
  target_chapter: 50
```

**约束**：
- `chapter_state.status` 枚举值：DIRECTION | WRITING | COMPLETED
- `chapter_state` 由 Orchestrator 在写章节过程中写入
- `current` 的累计统计字段（total_words、total_chapters_written）由 StateManager 在章节锁定后更新
- `state_version` 由 StateManager 独占维护，每次状态事务 +1；Orchestrator 不修改此字段
- `chunk_plan` 块的存在与否控制写章节模式：缺失 → 旧逐段模式；存在 → 节拍 LOOP 模式

---

## 二、author.yaml

作者视角——作者知道但角色和读者不一定知道的信息。

```yaml
# author.yaml
secrets:                        # 尚未揭示的秘密
  - id: "sec-001"
    content: "主角的系统实际上是XX文明的遗产"
    planned_reveal_chapter: 50
    status: "hidden"            # hidden | hinted | revealed
    hinted_at: []               # 哪些章节暗示过

  - id: "sec-002"
    content: "配角的真实身份是XX"
    planned_reveal_chapter: 30
    status: "hinted"
    hinted_at: [15, 22]

future_events:                  # 已规划但未发生的关键事件
  - id: "evt-001"
    description: "主角首次使用系统隐藏功能"
    planned_chapter: 12
    prerequisites: ["主角完成新手任务"]

author_notes: |                 # 自由备注
  第20章左右需要开始铺垫第二条主线。
```

**约束**：
- `secrets[].status` 只能取 `hidden | hinted | revealed`
- State Manager 在每章后将 `status: revealed` 的秘密归档到 `state/archive/`

---

## 三、reader.yaml

读者视角——读者已知什么、在猜什么。

```yaml
# reader.yaml
known_facts:                    # 读者已确认的事实
  - "主角拥有XX系统"
  - "系统可以发布任务并给予奖励"
  - "XX是主角的盟友"

suspicions:                     # 读者正在猜测的方向
  - topic: "系统的真正目的"
    confidence: 60              # 0-100，读者认为这个猜测正确的概率
    based_on: [3, 7, 11]        # 哪些章节提供了线索
    competing_theories:
      - "系统是敌对势力的陷阱"
      - "系统是主角自身的隐藏能力"

  - topic: "神秘配角的身份"
    confidence: 30
    based_on: [5, 9]

open_questions:                 # 读者脑中当前最想问的问题
  - "系统为什么选中主角？"
  - "XX角色到底站在哪边？"

reading_tension:                # 当前追读张力
  主线推进: 70                  # 0-100
  关系期待: 50
  悬念压力: 65
  升级期待: 80
```

**约束**：
- `suspicions[].confidence` 范围 0-100
- State Manager 每章更新，信息释放节奏由用户方向讨论确定

---

## 四、character.yaml

各 POV 角色的认知状态。

```yaml
# character.yaml
characters:
  - id: "char-001"
    name: "主角名"
    is_pov: true
    surface:                     # 静态角色属性（从 setting/characters/ 同步，写作时用于对话/动作一致性）
      speech_pattern: "简短/直接/不解释"
      mannerisms: "思考时摸下巴"
    current_state:
      location: "XX城"
      physical: "健康"
      emotional: "焦虑——刚发现系统的隐藏规则"
      level: "筑基期"            # 本作品的能力等级体系
      resources: ["XX法宝", "300灵石"]
    constraints:                 # 角色硬约束（Critic 的 pov_constraints 来源）
      cannot_do: ["暴露系统存在"]
      cannot_know: ["系统的真正来源", "盟友的真实身份"]
      cannot_change: ["不能突然变得优柔寡断"]
    knowledge:                   # 该角色知道什么
      known: ["系统的基本功能", "XX是盟友", "XX在追踪自己"]
      unknown: ["系统的真正来源", "盟友的真实身份"]
      misconceptions:            # 该角色的误判
        - topic: "XX的动机"
          believes: "XX想帮助自己"
          truth: "XX在利用自己获取系统权限"
    goals:
      current: "完成系统第10个任务，获得下一阶段权限"
      long_term: "成为XX级别的强者"
    pressures:
      - source: "系统任务时限"
        level: 70                # 0-100
      - source: "XX势力的追捕"
        level: 50
    relationships:               # 与其他角色的关系
      - with: "char-002"
        type: "盟友/怀疑"
        dynamic: "信任正在建立，但仍有保留"
        last_change_chapter: 9

  - id: "char-002"
    name: "配角名"
    is_pov: false
    surface:                     # 静态角色属性（写作配角对话/动作时用）
      speech_pattern: "急促/省略/用词古怪"
      mannerisms: ""
    current_state:
      location: "未知"
      physical: "健康"
    knowledge:
      known: ["主角拥有非凡能力"]
      unknown: ["主角能力的来源"]
```

**约束**：
- 只有 `is_pov: true` 的角色需要维护完整的 `knowledge` 块
- 非 POV 角色只需 `surface`、`current_state` 和简要 `knowledge`
- `pressures[].level` 范围 0-100
- `surface` 与 `constraints` 为静态属性，由 StateManager 在初始化/世界观构建时从 `setting/characters/xxx.yaml` 同步；worldbuilding 新增/修改角色时同步更新
- `tags` 为静态属性，仅存于 `setting/characters/xxx.yaml`（见 architect 角色档案模板），**不冗余进 character.yaml**；写作/检查时由 Orchestrator 从静态档案提取进交接包（见 handoff-schema 的 `character_tags`）
- 非 POV 角色可省略 `constraints`（Critic 的 pov_constraints 只针对 POV 角色）
- 生命周期结算见「九」：连续 30 章未出场的非 POV 角色指针化进 `state/archive/`

---

## 五、foreshadow.yaml

伏笔追踪——所有埋线和回收状态。

```yaml
# foreshadow.yaml
threads:
  - id: "thr-001"
    content: "玉佩上的裂纹会在关键时刻发光"
    planted_chapter: 3
    status: "active"             # active | touched | revealed | resolved | abandoned | stale
    type: "物件"                 # 物件 | 人物 | 信息 | 能力 | 关系
    priority: "high"             # high | medium | low
    touched_chapters: [7, 15]    # 轻碰但未揭示的章节
    resolved_chapter: null
    resolution: ""
    links_to: ["thr-003"]        # 关联的其他伏笔

  - id: "thr-002"
    content: "系统偶尔会发布看似无关的任务"
    planted_chapter: 5
    status: "touched"
    type: "信息"
    priority: "high"
    touched_chapters: [8, 12]
    resolved_chapter: null
    links_to: ["thr-005"]

  - id: "thr-003"
    content: "XX角色每次提到某个话题就转移视线"
    planted_chapter: 6
    status: "resolved"
    type: "人物"
    priority: "medium"
    resolved_chapter: 20
    resolution: "该角色是XX势力的卧底，怕被识破"

stats:
  total_planted: 8
  active: 5
  resolved: 2
  abandoned: 1                 # 已放弃（记录原因）
```

**约束**：
- `status` 只能取 `active | touched | revealed | resolved | abandoned | stale`（`stale` = 超过 30 章未触碰的活跃伏笔，由 State Manager 标记）
- Writer 每章从 `active + touched` 中选择 0-2 条进行轻碰
- 生命周期结算见「九」：`resolved` / `abandoned` / `stale` 指针化进 `state/archive/`
- 每 5 章检查是否有超过 30 章未触碰的活跃伏笔

---

## 六、agent-log.yaml

Agent 运行日志——断点恢复和调试用。

```yaml
# agent-log.yaml
entries:
  - timestamp: "2026-01-15T10:00:00"
    workflow: "write-chapter"
    chapter: 11
    from_agent: "Orchestrator"
    to_agent: "Writer"
    status: "in_progress"
    output: "方向已确认，逐段写作中"

  - timestamp: "2026-01-15T10:20:00"
    workflow: "write-chapter"
    chapter: 11
    from_agent: "Writer"
    to_agent: "Orchestrator"
    status: "completed"
    output: "整章完成，state_delta 汇总"

  - timestamp: "2026-01-15T10:25:00"
    workflow: "write-chapter"
    chapter: 11
    from_agent: "Orchestrator"
    to_agent: "StateManager"
    status: "completed"
    output: "用户锁定确认，状态已更新"

last_checkpoint:
  workflow: "write-chapter"
  chapter: 11
  agent: "StateManager"
  timestamp: "2026-01-15T10:25:00"
```

**约束**：
- Orchestrator 在每次 Agent 切换时写入
- `last_checkpoint` 用于断点恢复——Orchestrator 启动时读最后一条
- Agent 异常中断时 `status: error`，记录错误信息

---

## 七、文件版本与兼容

### 版本演进

| schema_version | 特征 | 状态 |
|----------------|------|------|
| 1 | 中文数字目录（`00-书核/`、`90-状态/`）+ 作品总表 + 硬设定 | 已废弃 |
| 2 | 英文目录 + `core/作品总表.md` + `setting/硬设定.yaml` + `files.hard_canon` + `outline/全书总纲.md` | 需升级 |
| 3（当前） | `core/作品核心.md` + `setting/硬规则.yaml` + `files.hard_rules` + `outline/全书总纲.yaml` + `workspace.chapter_word_target` | 当前 |

### 兼容规则

- 所有 YAML 文件使用 YAML 1.2 规范
- 字段新增向后兼容——读取方忽略未知字段
- 字段删除需在 State Manager 中做迁移（旧字段 → 归档）
- 必填字段缺失时，Agent 拒绝启动并报告 Orchestrator
- `schema_version`（结构版本，v1/v2/v3）与 `state_version`（事务版本，整数递增）是两个独立字段：前者只在工作区升级时变更，后者每次状态更新都递增。区分详见「八」

### 升级触发

- `progress.yaml` **缺失 `schema_version` 字段**（且 `files` 块使用旧字段 `hard_canon`、`files.outline` 指向 `.md`）→ 判定为 v2 旧工作区，Orchestrator 检测到后引导用户执行 `/novel-studio:upgrade`（见 `workflow-specs/upgrade-project.md`）
- 升级只改 `core/`、`setting/`、`outline/` 路径与 `progress.yaml` 结构，**保留 `state/` 下 author/reader/character/foreshadow 大文件**（续写上下文不可丢）
- 升级完成后写入 `schema_version: 3`

---

## 八、事务版本与变更日志

> 状态系统用「事务版本」对抗历史记忆干扰——过时状态残留、多文件更新不同步、无版本可回溯、旧状态覆盖新状态。机制只有两项：一个版本号 + 一份变更日志。

### 8.1 两个概念

| 概念 | 文件 | 字段 | 维护者 | 含义 |
|------|------|------|--------|------|
| 全局事务版本号 | progress.yaml | `state_version` | StateManager | 状态系统总版本，每次状态更新 +1 |
| 事务日志 | transaction-log.yaml | `transactions` | StateManager | 每次事务改了什么（何时/因哪章/改了哪些文件） |

**与 `schema_version` 的区别**：`schema_version` 是文件**结构**版本（v1/v2/v3），只在工作区升级时变；`state_version` 是状态**内容**的事务版本，每次状态更新都递增。二者互不影响。

### 8.2 transaction-log.yaml

StateManager 独占写入。与 `agent-log.yaml` 的职责边界：`agent-log` 由 Orchestrator 记录**流转**（谁调了谁、进行到哪步），本文件由 StateManager 记录**状态变更**（改了什么）。

```yaml
# transaction-log.yaml
transactions:
  - txn: 15                     # 事务号，与 progress.state_version 一致
    chapter: 11                 # 触发事务的章节；init/compress 事务为 null
    trigger: "write"            # write | revise | worldbuild | init | compress
    files_changed:              # 本次事务改动的文件
      - character.yaml
      - foreshadow.yaml
      - reader.yaml
    summary: "主角进阶，thr-001 轻碰，读者获知新线索"   # 一句话改动摘要
```

**约束**：
- `transactions[].txn` 从 1 起递增，与 `progress.state_version` 保持一致
- `summary` 是一句话摘要，不做字段级 diff——精细的章节锚点由各状态文件自带的 `touched_chapters`/`last_change_chapter`/`hinted_at` 承担
- 事务日志同样会瘦身（见 `memory-compress.md`），只保留最近 30 章记录，更早归档到 `state/archive/transaction-log-archive.yaml`

### 8.3 一致性核对（写前）

StateManager 每次写入前核对：`transaction-log` 最后一条 `txn` 是否等于 `progress.state_version`。

- 不等 → 上次事务没写完（中断），报告 Orchestrator 重新执行 state_delta（幂等），不做精细回滚
- 相等 → 事务正常开始

**四种干扰的应对**：
- 过时状态残留：变更日志可追溯「哪个文件/条目最后一次是哪章改的」，压缩时据此清理 stale
- 多文件更新不同步：事务号对齐检测「上次事务是否完整」，中断则幂等重跑
- 无版本可回溯：`state_version` + 变更日志构成时间线
- 旧状态覆盖新状态：StateManager 无状态、每次读磁盘，写前核对事务号即可拦截中断重启带来的旧覆盖

### 8.4 事务范围

写章节、修订、worldbuild 同步、初始化、记忆压缩各算一次事务，每次独立递增 `state_version`。同一次事务改动的多个文件共享同一个事务号。

---

## 九、状态对象生命周期

> 状态文件的定位：**活跃索引**，不是历史档案。它只回答一个问题——「下一章还用得上吗」。完整历史在正文 `chapters/`（唯一真相）和卷记忆（结构化摘要），状态文件只保留活跃集。这条原则适用于现在与未来的所有状态文件，膨胀问题统一归结到同一个判断。

### 9.1 统一模型

所有状态文件都是「活跃对象表」，每个对象走同一条生命周期：

```
active（完整条目）──「下一章还用得上吗？」──> settled（指针）
```

- **active**：下一章可能用到的对象 → 留在主文件，保留完整条目。
- **settled**：用不上了 → 降级为一行指针进 `state/archive/`，**不复制详情**。

指针固定三项：`id + 一句话摘要 + 最后相关章节号`。需要完整细节时，按章节号回查正文/卷记忆重建，不回写状态文件。

### 9.2 各文件结算时机

| 文件 | 保留（active） | 指针化（settled） |
|------|---------------|------------------|
| foreshadow.yaml | `active` / `touched`（未收束） | `resolved` / `abandoned` / `stale` |
| character.yaml | POV 角色完整 + 本卷出场配角 | 连续 30 章未出场（含退场） |
| reader.yaml | 读者现在在猜/在问的 | 已解答疑问 / 已落定猜测 |
| author.yaml | 未揭示秘密 + 未发生未来事件 | `revealed` 秘密 / 已发生未来事件 |

### 9.3 三条配套规则

1. **结算一句话判断**：「下一章还用得上吗」。用 → 留；不用 → 指针化。
2. **残留信息不归压缩管**：伏笔收束后仍影响后文的「影响」，不靠压缩反向推断，由日常 `state_delta` 自然落到 `reader.known_facts` / `author.secrets`。压缩只做「指针化」，不猜语义。
3. **归档指针化，永不膨胀**：archive 条目固定 `id + 一句话 + 章节号`（几十字节），不存第二份真相。

---

## 十、chunk 字段定义与生命周期

> 写章节的「节拍批量确认 Loop」模式的运行时状态。`progress.yaml` 的 `chunk_plan` 块是该模式**唯一状态源**；chunk 设计内容（beat 定义、选项池）由 `outline/chunks/chunk-XX.yaml` 提供，是**静态设计文档**，不重复存储于 state。

### 10.1 块结构

```yaml
chunk_plan:
  # 当前 chunk 标识与来源
  current_chunk: "chunk-01"        # 当前 chunk id；null = 未启动 chunk
  source: "outline/chunks/chunk-01.yaml"   # chunk 设计文件

  # 当前正在处理的节拍
  current_beat: "beat-3"           # 当前 beat id；null = chunk 全部完成

  # chunk 范围
  chapter_range: [11, 15]         # [起始章, 结束章]
  chapter_word_target: 2000        # 单章目标字数（继承自 workspace，可覆盖）

  # ★ 节拍确认状态（核心数据结构，详见 10.3）
  confirmed_beats:
    "beat-1":
      choice: "选项A：接上章结尾"
      source: "option"             # option | custom | tweak:<选项> | ai_improvised
      locked: true                 # true = 已锁定；false = 已呈现未锁；缺失 key = 还没呈现
      locked_at: "2026-01-15T10:30:00"

  # 状态机字段
  loop_state: "WRITING"           # LOOP | WRITING | REVIEW | LOCKED
  loop_iteration: 2               # LOOP 重入次数（含首次进入）
  loop_entered_at: "2026-01-15T10:30:00"

  # 写作进度（当前章节维度）
  beats_written: 2                # 当前章节已写完的 beat 数
  beats_total: 7                  # 当前章节的 beat 总数（非 chunk 全部）
  words_written: 850              # 当前章节已写累计字数
  writing_started_at: "2026-01-15T10:36:00"

  # 回退日志（详见 10.5）
  loop_revert_log:
    - beat_id: "beat-3"
      reverted_at: "2026-01-15T11:30:00"
      reason: "用户指出方向偏离了卷节拍"
```

### 10.2 loop_state 状态机

```
LOOP ────► WRITING ────► REVIEW ────► WRITING ────► ... ────► LOCKED
  ▲                       │                                            ▲
  │                       ▼                                            │
  └───────────── (任意阶段用户说"回到 LOOP") ──────────────────────────┘
```

| 状态 | 含义 | Orchestrator 动作 |
|------|------|------------------|
| `LOOP` | 批量确认节拍中（chunk 启动时，或用户主动重入） | 展示未确认 beat 的选项，接收用户输入 |
| `WRITING` | Writer 正在写当前 beat | 把 beat 任务打成 WriterBrief-Beat，调度 Writer |
| `REVIEW` | Writer 写完 beat 后等用户检查（chunk_mode 控制粒度） | 展示内容等用户指令 |
| `LOCKED` | chunk 全部章节完成 | 触发 StateManager 收尾事务（archive + 清空 chunk_plan） |

### 10.3 节拍确认状态的四种语义

用同一字段表达，靠 `confirmed_beats` 中是否存在 key + `locked` 字段值区分：

| 状态 | 数据形态 |
|------|---------|
| 未呈现 | 该 beat_id 不在 `confirmed_beats` 中 |
| 已呈现未锁 | 该 beat_id 在 `confirmed_beats` 中，`locked: false` |
| 已锁定 | 该 beat_id 在 `confirmed_beats` 中，`locked: true` |
| 已写完 | `beats_written` 已计入该 beat，但 `confirmed_beats` 保留 |

`confirmed_beats[].source` 枚举：
- `option`：用户从预设选项池中选了 A/B/C/D
- `custom`：用户自定义方向
- `tweak:<原选项>`：用户选了某个选项但改了措辞（如 `tweak:选项B`）
- `ai_improvised`：Writer 在用户未选的情况下自己发挥（仅当用户选 D「你来定」时）

### 10.4 写入权约束

**Orchestrator** 写入的字段（写章节流程中）：
- `current_chunk`、`current_beat`、`confirmed_beats`、`loop_state`、`loop_iteration`、`loop_revert_log`
- `beats_written`、`words_written`、`writing_started_at`
- `source`、`chapter_range`、`chapter_word_target`

**StateManager** 写入的字段：
- 章节事务中：递增 `beats_written` 与 `words_written`；**不修改** `confirmed_beats`、`loop_state`、`loop_revert_log`
- chunk 收尾事务（loop_state: LOCKED 触发时）：清空 `chunk_plan` 全部字段为 null/0

**写入互斥**：
- 章节事务中不能动 `chunk_plan.confirmed_beats`（已用节拍不能回收）
- StateManager 不写 `loop_revert_log`（这是 LOOP 行为记录）

### 10.5 LOOP 回退机制

任意状态下用户说"回到 LOOP" / "改 beat-X" / "这个 beat 方向不对"：

1. Orchestrator 把 `loop_state: LOOP`
2. `loop_iteration +1`
3. 目标 beat 的 `confirmed_beats` 条目：
   - **未写**（`beats_written` 未计）：`locked: false`（让用户重选）
   - **已写**：`locked: true` 保留，但 `loop_revert_log` 追加一条

`loop_revert_log` 每条结构：

```yaml
- beat_id: "beat-3"
  reverted_at: "2026-01-15T11:30:00"
  reason: "用户指出方向偏离了卷节拍"   # 可选，用户口述或 Orchestrator 推断
```

### 10.6 chunk 完成清理

StateManager 在最后一章 `COMPLETED` 触发时检测（**双重条件**）：
- `current.chapter == chapter_range[1]`（最后一章）
- `chapter_state.status: COMPLETED`
- `beats_written == beats_total`（注：`beats_total` 是当前章的 beat 数）

满足 → 触发「chunk 收尾事务」：
1. `outline/chunks/chunk-XX.yaml` 内容指针化进 `state/archive/chunks-archive.yaml`
2. `progress.yaml` 的 `chunk_plan` 块字段全部置 null / 0（保留字段结构）
3. `transaction-log.yaml` 追加 `trigger: "chunk_close"` 记录
4. `state_version` 独立 +1（与章节事务分开）
5. `outline/chunks/chunk-XX.yaml` 文件**不删除**（保留为大纲设计真值）

### 10.7 chunk 跨卷约束

- chunk **不跨卷**：`chapter_range` 必须完全落在某一卷的 chapter_range 内
- 跨卷时强制拆分：`chunk-XX` 覆盖 `[V1_last_chapter]`、`chunk-XX+1` 覆盖 `[V2_first_chapter, ...]`
- 拆分点在 LOOP 启动前由 Orchestrator 检测并提示用户

### 10.8 兼容性（缺失 chunk_plan 块的旧工作区）

- `schema_version` 保持 3（字段新增向后兼容，旧读取方忽略未知字段）
- 缺失 `chunk_plan` 块的旧工作区 → Orchestrator 检测后降级到旧逐段模式（保留 `/novel-studio:write N` 命令可用）
- 升级路径：`/novel-studio:upgrade` 检测到缺 `chunk_plan` 块 → 询问用户是否启用节拍模式 → 用户确认后 StateManager 写入空 `chunk_plan: {}`

---

## 十一、文件版本与兼容（已上移至第七节）

本节仅补充：`chunk_plan` 块是 schema_version=3 的可选扩展块。缺失不影响旧读取方（schema_version 读取规则不变）。
