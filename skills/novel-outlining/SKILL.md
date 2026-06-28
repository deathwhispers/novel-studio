---
name: novel-outlining
description: "中文小说结构规划 skill。用于把 premise 和设定扩展成完整主线、幕结构、分卷计划、章节 beats、伏笔安排和回收节奏，适用于“帮我列大纲”“做分卷规划”“拆成章节计划”“安排伏笔回收”“中途改纲但不想推翻整本书”等场景。"
---

# Novel Outlining

## Overview

把小说从“能讲”变成“能持续推进”。这个 skill 负责结构承诺，不负责一次性把正文写完，并且要根据长篇或短篇形态调整规划粒度。

## 大纲阶梯

按从粗到细的顺序工作：

1. 主线与结局方向
2. act 或 volume 级结构
3. 每卷起止状态变化
4. 章节 beats
5. 伏笔埋设与回收位置

短篇时可以压缩为：

1. 题眼
2. 关键推进
3. 转折
4. 收束或回响

## 主要产物

- `20-outline/master-outline.md`
- `20-outline/arc-tracker.md`
- `20-outline/volumes/*.md`
- `20-outline/chapter-beats/*.md`
- `20-outline/causality/scene-causality-map.md`
- `20-outline/payoff-tracking/payoff-ledger.md`

## 章节 beat 最低要求

每一章至少要写清：

- POV
- scene objective
- obstacle or opposition
- turn or revelation
- emotional shift
- end hook
- continuity load
- payoff threads touched

如果目标是提高写作质量，还要把这些信息同步进两张表：

- `scene-causality-map.md`
- `payoff-ledger.md`

## 改纲原则

- 尽量做局部改纲，不轻易重置整本书。
- 改纲后明确指出哪些卷、哪些章节 beats 需要联动修改。
- 如果用户只想写下一章，不要把任务扩大成重列整本书。
- 长篇优先保留留存循环，短篇优先保留题眼和结尾力量。
- 改纲时不要只改 beats，要同步检查因果链表和伏笔回收表是否失效。

## 资源

需要模板与分层方式时，读取 `references/outline-ladder.md`。

大纲必须能继续写，不只是看起来完整。
