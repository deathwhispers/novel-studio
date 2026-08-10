# 状态文件 Schema

> 定义工作区 `state/` 下所有 YAML 文件的结构和字段约束。State Manager 是本文件定义的唯一实现者。

---

## 一、progress.yaml

工作区当前进度索引。

```yaml
# progress.yaml
workspace:
  name: "作品名称"
  genre: "番茄系统爽文"         # 品类标识，关联 genres/ 下的配方
  mode: "商业连载"              # 商业连载 | 类型长篇 | 文学叙事 | 短篇 | 探索起草
  created: "2026-01-01"

current:
  chapter: 10                   # 当前已完成的最后一章编号
  volume: 1                     # 当前卷号
  total_chapters_written: 10
  total_words: 25000
  last_updated: "2026-01-15T10:30:00"

chapter_state:                  # 当前正在写的章节状态（write-chapter workflow 用）
  chapter_number: 11
  status: "NEED_SCENE"          # NEED_PLAN | NEED_SCENE | NEED_DRAFT | NEED_REVIEW | COMPLETED
  story_contract: ""            # 文件路径，NEED_PLAN 之后填充
  scene_contract: ""            # 文件路径，NEED_SCENE 之后填充
  draft: ""                     # 文件路径，NEED_DRAFT 之后填充
  review_report: ""             # 文件路径，NEED_REVIEW 之后填充

files:
  book_core: "core/作品总表.md"
  hard_canon: "setting/硬设定.yaml"
  outline: "outline/全书总纲.md"
  volumes:
    - "outline/volumes/volume-01.yaml"
  chapters_dir: "chapters/"

next_milestone:
  type: "卷末"                  # 卷末 | 中段审视 | 完本
  target_chapter: 50
```

**约束**：
- `chapter_state.status` 只能取枚举值
- `chapter_state` 在 write-chapter workflow 中由 Orchestrator 写入
- `current` 在每次 State Manager 完成后更新

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
- State Manager 每章更新，Director 读取后决定信息释放节奏

---

## 四、character.yaml

各 POV 角色的认知状态。

```yaml
# character.yaml
characters:
  - id: "char-001"
    name: "主角名"
    is_pov: true
    current_state:
      location: "XX城"
      physical: "健康"
      emotional: "焦虑——刚发现系统的隐藏规则"
      level: "筑基期"            # 本作品的能力等级体系
      resources: ["XX法宝", "300灵石"]
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
    current_state:
      location: "未知"
      physical: "健康"
    knowledge:
      known: ["主角拥有非凡能力"]
      unknown: ["主角能力的来源"]
```

**约束**：
- 只有 `is_pov: true` 的角色需要维护完整的 `knowledge` 块
- 非 POV 角色只需 `current_state` 和简要 `knowledge`
- `pressures[].level` 范围 0-100
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
    status: "active"             # active | touched | revealed | resolved
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
- `status` 只能取 `active | touched | revealed | resolved | abandoned`
- Director 每章从 `active + touched` 中选择 0-2 条进行轻碰
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
    to_agent: "Director"
    status: "completed"
    output: "Story Contract 已生成"
    file: "outline/volumes/chapter-11-contract.yaml"

  - timestamp: "2026-01-15T10:05:00"
    workflow: "write-chapter"
    chapter: 11
    from_agent: "Director"
    to_agent: "Scene Planner"
    status: "completed"
    output: "Scene Contract 已生成"

  - timestamp: "2026-01-15T10:20:00"
    workflow: "write-chapter"
    chapter: 11
    from_agent: "Scene Planner"
    to_agent: "Writer"
    status: "in_progress"

last_checkpoint:
  workflow: "write-chapter"
  chapter: 11
  agent: "Writer"
  timestamp: "2026-01-15T10:20:00"
```

**约束**：
- Orchestrator 在每次 Agent 切换时写入
- `last_checkpoint` 用于断点恢复——Orchestrator 启动时读最后一条
- Agent 异常中断时 `status: error`，记录错误信息

---

## 七、文件版本与兼容

- 所有 YAML 文件使用 YAML 1.2 规范
- 字段新增向后兼容——读取方忽略未知字段
- 字段删除需在 State Manager 中做迁移（旧字段 → 归档）
- 必填字段缺失时，Agent 拒绝启动并报告 Orchestrator
