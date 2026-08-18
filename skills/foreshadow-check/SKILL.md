---
name: foreshadow-check
description: "伏笔追踪检查。检查新埋伏笔是否登记、旧伏笔是否遗忘、回收是否合理。纯能力，由 Critic Logic Checker 调用。"
category: analysis
---

# 伏笔追踪检查

## 能力范围

- 检查新出现的伏笔是否已标记
- 检查是否有超过 30 章未触碰的遗忘伏笔
- 检查回收是否合理（不硬回收）

## Writer 侧：标记新伏笔

在 `state_delta` 中标记本章新埋的伏笔：

```yaml
new_threads_planted:
  - content: "玉佩在主角使用新能力时发烫"
    type: "物件"
    priority: "high"
    links_to: []           # 关联已有伏笔的 id
```

## Critic 侧：伏笔状态检查

### 检查项

- [ ] 本章中是否有明显是伏笔但 Writer 未在 `new_threads_planted` 中标记的？
- [ ] 是否有应该在本章回收（按大纲计划）但未回收的伏笔？
- [ ] 回收方式是否合理？

### 伏笔回收合理性

| 问题 | 检测 |
|------|------|
| 硬回收 | 回收时强行追溯解释，前面找不到暗示 |
| 太早回收 | 埋了不到 3 章就回收——读者还没记住 |
| 太晚回收 | 超过 30 章未触碰——读者已忘记 |
| 回收无感 | 回收时没有任何戏剧效果——像走流程 |

## 输出格式

```yaml
foreshadow_report:
  unregistered:
    - location: "场景3"
      description: "被救者临别前看了一眼主角的玉佩——可能是新伏笔，Writer 未标记"
  forgotten_check:
    stale_threads: []
    overdue_reveals: []
  recovery_quality:
    - thread_id: "thr-003"
      recovery_chapter: 11
      issue: "回收方式平淡——角色台词中顺带解释，缺乏戏剧性"
```

## 伏笔的状态流转

```
planted → active（等待触碰）
       → touched（轻碰了一次，读者应该还有印象）
       → revealed（线索已给出，真相即将揭示）
       → resolved（已回收，保留摘要）
       → archived（移入归档）
```
