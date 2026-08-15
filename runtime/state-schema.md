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

files:
  book_core: "core/作品核心.md"
  hard_rules: "setting/硬规则.yaml"
  outline: "outline/全书总纲.yaml"
  volumes:
    - "outline/volumes/volume-01.yaml"
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
- 非 POV 角色可省略 `constraints`（Critic 的 pov_constraints 只针对 POV 角色）
- State Manager 每 5 章压缩非 POV 角色状态

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
- State Manager 在伏笔 resolve 后保留一行摘要，删除详细描述
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

- `progress.yaml` **缺失 `schema_version` 字段**（且 `files` 块使用旧字段 `hard_canon`、`files.outline` 指向 `.md`）→ 判定为 v2 旧工作区，Orchestrator 检测到后引导用户执行 `/novel-studio:upgrade`（见 `workflows/upgrade-project.md`）
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
