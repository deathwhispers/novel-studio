---
type: command
name: write
description: "写指定章节。自动流转完整流水线：Director → ScenePlanner → Writer → Critic → StateManager。"
workflow: write-chapter
---

# /novel-studio:write

写指定章节。自动运行完整 5 阶段流水线。

## 用法

```
/novel-studio:write <章节号>
/novel-studio:write next          # 写下一章（自动计算章节号）
/novel-studio:write               # 等同于 /novel-studio:write next
```

## 执行流程

1. **Orchestrator** 多轮确认（1-2 个问题确认本章方向）
2. **Director** 设计 Story Contract（本章功能 + 信息释放 + 禁止触碰）
3. **ScenePlanner** 设计 Scene Contract（每场景五拍骨架）
4. **Writer** 写正文（在约束内连续起草）
5. **Critic** 5 Checker 质量验收
6. **StateManager** 更新所有状态（通过后）

中间不需要用户干预。

## 示例

```
/novel-studio:write 10

✍️ 正在确认第10章方向…
✅ 本章功能：推进（主角首次使用新能力）
   信息释放：可揭示新能力效果，禁止触碰系统来源
   章尾钩子：系统弹出前所未有的任务类型

🎬 正在设计场景结构…
✅ 3 个场景已编排（钩子→主体冲突→收束）

📝 正在写作中…
✅ 第10章完成（2800字）

🔍 正在质量检查…
✅ 通过（AI味 2 处已修复，无硬伤）

📋 状态已更新 → 第10章完结。随时可以 /novel-studio:write 11
```

## 快速通道

如果用户给出了完整的章节方案（剧情路径 + 爽点方向 + 关键场景）→ Orchestrator 一句话确认后直接启动流水线，跳过确认轮。

## 断点恢复

如果上一次 `/novel-studio:write` 未完成（中断/异常）→ 重新执行时自动从断点继续。例如 Writer 写到一半中断 → 输入 `/novel-studio:write 10` → 从 NEED_DRAFT 状态继续 Writer。
