# 记忆压缩协议

> State Manager 每 5 章或卷末执行的记忆压缩操作规范。目标：控制 `state/` 总大小在可加载范围内，同时保留足够上下文供续写决策。压缩本身也是一次状态事务（trigger: compress）——执行完成后递增 `progress.state_version`、记 transaction-log（见 state-schema 第八节）。
>
> **压缩 = 生命周期结算**：把「下一章用不上」的对象从主文件指针化进 `state/archive/`。统一模型见 state-schema 第九节，本文件只讲「怎么执行」。

---

## 一、触发条件

| 条件 | 触发时机 |
|------|---------|
| `current.chapter % 5 == 0` | 第 5/10/15/20... 章完成后 |
| 卷末 | 当前卷最后一章完成后（无论是否 5 的倍数） |
| `state/` 总大小 > 50KB | 紧急压缩（任意章节完成后） |
| `state/` 总大小 > 80KB | **轻量压缩**（A7 修复——Orchestrator 启动时触发；区别于正常压缩，见第五节） |
| `author_notes` 单次增量 > 200 字 | **下次章节事务内联压缩**（不等到第 5 章）——O7 修复 |

**为什么 author_notes 需要即时触发**：作者备忘是高时效信息（"第 20 章左右开始铺垫第二条主线"），积压到第 5 章才处理可能导致新加的备忘被旧内容覆盖丢失。即时压缩=把增量超过 200 字的部分立刻指针化进 `state/archive/author-notes-archive.yaml`，保留摘要 + 完整备份指针。

---

## 二、结算规则

对每个状态文件，逐对象问一句：**「下一章还用得上吗」**。

| 文件 | 保留（active） | 指针化（settled → archive） |
|------|---------------|---------------------------|
| foreshadow.yaml | `active` / `touched` | `resolved` / `abandoned` / `stale` |
| character.yaml | POV 完整 + 本卷出场配角 | 连续 30 章未出场（含退场） |
| reader.yaml | 读者现在在猜/在问的 | 已解答疑问 / 已落定猜测 |
| author.yaml | 未揭示秘密 + 未发生未来事件 | `revealed` 秘密 / 已发生未来事件 |

**指针格式**（archive 统一条目，固定三项）：

```yaml
- id: "thr-003"
  summary: "XX角色是XX势力的卧底，怕被识破"
  chapter: 20          # 最后相关章节，回查正文/卷记忆用
```

不复制完整详情——细节按 `chapter` 回查正文，状态文件不是第二份真相。

---

## 三、结算执行

### 3.1 foreshadow.yaml

`resolved` / `abandoned` / `stale` 的伏笔 → 指针化进 `state/archive/`；`active` / `touched` 保留完整条目。

### 3.2 character.yaml

- 非 POV 角色连续 30 章未出场 → 指针化进 `state/archive/inactive-characters.yaml`
- POV 角色与本卷出场配角保留完整条目

### 3.3 reader.yaml

- `open_questions` 已被正文解答 → 指针化进 `state/archive/answered-questions.yaml`
- `suspicions` 已落定 → 证实（confidence > 70）的移入 `known_facts`，证伪（confidence < 20 且 10 章未更新）的指针化
- `known_facts` 超 20 章 → 合并为一段 `reading_summary`

### 3.4 author.yaml

- `secrets` 中 `revealed` → 指针化进 `state/archive/revealed-secrets.yaml`
- `future_events` 已发生 → 指针化
- `author_notes` 超 500 字 → 提取摘要，详细内容指针化进 `state/archive/author-notes-archive.yaml`
- **`author_notes` 单次增量 > 200 字**（即时触发，下次章节事务内联压缩）→ 增量部分直接指针化进 archive，不做摘要——保留完整时序

---

## 四、卷记忆生成

每卷结束时生成 `state/卷记忆/第X卷-摘要.md`：

```markdown
# 第X卷摘要

## 卷信息
- 章节范围：第 X 章 ~ 第 Y 章
- 字数：约 Z 万
- 写作时间：YYYY-MM-DD ~ YYYY-MM-DD

## 关键事件（最多 10 条）
1. 第 A 章：主角获得XX能力
2. 第 B 章：XX角色背叛
...

## 本卷揭示的秘密
- sec-001：XX角色的真实身份（第 C 章）
- sec-003：系统的隐藏功能（第 D 章）

## 本卷新增活跃伏笔
- thr-010：XX物件在第 E 章出现异常
- thr-011：XX势力在第 F 章露出端倪

## 卷末角色状态快照
- 主角：XX级，位于XX城，当前目标为XX。压力来源：XX(80%)
- POV配角A：位于XX，与主角关系从盟友变为怀疑。已知：XX。

## 卷末追读状态
- 读者最关心的问题：XX到底是什么？
- 下一卷读者最期待：主角与XX势力的正面对抗
```

**约束**：卷摘要控制在 500 行以内。

---

## 五、事务日志瘦身

`transaction-log.yaml` 是日志（不适用对象生命周期），只保留最近 30 章记录，更早的移入 `state/archive/transaction-log-archive.yaml`。

---

## 七、轻量压缩（A7 修复，trigger: compress_lightweight）

**与正常压缩的边界**：

| 维度 | 正常压缩（第五节 + 第六节） | 轻量压缩（A7 修复） |
|------|---------------------------|---------------------|
| 触发时机 | 第 5/10/15 章 + 卷末 + 紧急 >50KB | Orchestrator 启动时扫描 `state/` > 80KB |
| 触发方 | StateManager 在章节事务中自动检测 | Orchestrator 启动时 `state_size_check` 主动触发 |
| 操作范围 | 完整结算（4 个文件全部指针化 + 卷记忆生成） | 只清理 `state/archive/` 中超过 30 章的事务日志归档 |
| 动 active 字段？ | 是（4 文件全部扫一遍） | **否**（不动 author/reader/character/foreshadow 的 active 字段） |
| 动 chunk_plan？ | 否（章节事务后续接续 chunk 收尾） | **否**（不动 confirmed_beats / loop_revert_log） |
| 事务 trigger | `compress` | `compress_lightweight`（state-schema 第十节） |

**轻量压缩执行步骤**（StateManager 收到 Orchestrator 调度后）：

1. **只清理事务日志归档**——遍历 `state/archive/transaction-log-archive.yaml`，把超过 30 章的事务条目丢弃（保留最近 30 章条目）
2. **不动** `state/author.yaml`、`state/reader.yaml`、`state/character.yaml`、`state/foreshadow.yaml` 的 active 字段
3. **不动** `state/progress.yaml` 的 `chunk_plan.confirmed_beats` / `loop_revert_log`（活跃 chunk 需要）
4. **transaction-log 追加** `trigger: "compress_lightweight"` + `state_version +1`（独立事务）

**为什么不完整压缩**：完整压缩（>50KB 紧急）会结算大量对象指针化，对运行中 chunk 是侵入式操作。轻量压缩的目标是「不打断运行 + 减小体积」——只清理历史归档里的旧事务条目即可达到 80KB → <50KB 目标。

**触发链路**：

```
Orchestrator 启动 → state_size_check
  ├─ state/ ≤ 50KB → 无操作
  ├─ 50KB < state/ ≤ 80KB → 警告 + 继续
  ├─ 80KB < state/ < 100KB → 调度 StateManager 执行轻量压缩
  └─ state/ ≥ 100KB → 暂停 + 提示用户
```

StateManager 收到 `/lightweight-compress` 指令（详见 `agents/state-manager.md`）→ 按本节步骤执行 → 完成后 Orchestrator 重新启动。

---

## 六、结算后验证

State Manager 完成压缩后执行：

- [ ] `state/` 下所有文件总大小 < 50KB
- [ ] 每个 YAML 文件可正常解析
- [ ] 所有文件间的引用路径有效（不指向已删除文件）
- [ ] 版本一致：`transaction-log` 最后一条 `txn` 等于 `state_version`（压缩事务已完整提交）
- [ ] transaction-log.yaml 已记录本次压缩事务（trigger: compress，state_version 已递增）
- [ ] 归档目录 `state/archive/` 创建完成（如首次）
