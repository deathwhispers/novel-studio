# 记忆压缩协议

> State Manager 每 5 章或卷末执行的记忆压缩操作规范。目标：控制 `state/` 总大小在可加载范围内，同时保留足够上下文供 Director 决策。

---

## 一、触发条件

| 条件 | 触发时机 |
|------|---------|
| `current.chapter % 5 == 0` | 第 5/10/15/20... 章完成后 |
| 卷末 | 当前卷最后一章完成后（无论是否 5 的倍数） |
| `state/` 总大小 > 50KB | 紧急压缩（任意章节完成后） |

---

## 二、压缩操作

### 2.1 foreshadow.yaml 压缩

**操作**：
1. `status: resolved` 的伏笔保留一行摘要（id + content + resolved_chapter + resolution），删除 `touched_chapters` 详细列表和 `links_to`
2. `status: abandoned` 的伏笔移到 `state/archive/abandoned-threads.yaml`
3. 超过 30 章未触碰的 `active` 伏笔 → 标记为 `stale`，在文件中加注释提醒 Director

**压缩后格式**：
```yaml
resolved_summary:
  - id: "thr-003"
    content: "XX角色每次提到某个话题就转移视线"
    resolved: "第20章——该角色是XX势力的卧底"
```

### 2.2 character.yaml 压缩

**操作**：
1. 非 POV 角色的完整 `knowledge` 块压缩为一段摘要（已知/不知各一行）
2. 非 POV 角色的 `pressures` 只保留 level > 50 的项
3. POV 角色保留完整状态
4. 所有角色的 `relationships` 只保留 `dynamic` 和 `last_change_chapter`，删除详细描述

**压缩后格式**（非 POV 角色）：
```yaml
- id: "char-003"
  name: "配角名"
  is_pov: false
  summary: "XX城城主，对主角态度从敌对转为中立。已知主角拥有系统。当前无高压力。"
```

### 2.3 reader.yaml 压缩

**操作**：
1. `suspicions` 中 `confidence > 70` 的猜测 → 移到 `known_facts`
2. `suspicions` 中 `confidence < 20` 且超过 10 章未更新 → 删除
3. `open_questions` 中已被正文解答的问题 → 移到 `state/archive/answered-questions.yaml`
4. 将 `known_facts` 中超过 20 章的事实合并为一段摘要

**压缩后新增**：
```yaml
reading_summary: |
  读者已了解：主角拥有XX系统，可使用基本功能，系统正在引导主角完成进阶任务。
  读者最关心：系统的真正目的、神秘配角的身份。
  当前追读张力：主线推进70%，悬念压力65%。
```

### 2.4 author.yaml 压缩

**操作**：
1. `status: revealed` 的秘密 → 移到 `state/archive/revealed-secrets.yaml`
2. `planned_reveal_chapter` 已过的秘密 → 更新计划或标记延期
3. `author_notes` 超过 500 字 → 提取摘要，详细内容移到 `state/archive/author-notes-archive.yaml`

---

## 三、卷记忆生成

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

## 四、状态文件瘦身

每次压缩后执行：

1. `foreshadow.yaml` 中 `resolved_summary` 超过 10 条 → 最旧的移入归档
2. `character.yaml` 非 POV 角色摘要超过 15 个 → 超过 30 章未出场的角色移入 `state/archive/inactive-characters.yaml`
3. 所有 YAML 文件的总行数控制在 500 行以内（含卷记忆摘要引用）
4. 超出部分移入 `state/archive/`，在状态文件中保留引用路径

---

## 五、压缩后验证

State Manager 完成压缩后执行：

- [ ] `state/` 下所有文件总大小 < 50KB
- [ ] 每个 YAML 文件可正常解析
- [ ] 所有文件间的引用路径有效（不指向已删除文件）
- [ ] agent-log.yaml 记录本次压缩操作
- [ ] 归档目录 `state/archive/` 创建完成（如首次）
