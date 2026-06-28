---
name: novel-market-scan
description: "中文小说市场扫榜与趋势研究 skill。用于分析起点、番茄、晋江等平台的榜单、书名模式、题材组合、简介卖点、开篇钩子和平台差异，帮助用户决定写什么、写给谁、发到哪里。适用于“最近什么题材火”“帮我扫榜”“这个平台偏爱什么”“我该写长篇还是短篇”“哪些元素更有商业潜力”等场景。"
---

# Novel Market Scan

## Overview

先看市场，再决定题材与打法。这个 skill 的目标不是追热点本身，而是提炼可执行的商业机会与风险边界。

## 工作流程

1. 明确平台
   - 起点、番茄、晋江、知乎盐言、公众号短篇或用户指定平台
2. 明确目标
   - 找风口
   - 验证选题
   - 对比平台
   - 判断长篇/短篇策略
3. 提炼重复信号
   - 只把跨样本反复出现的模式视为有效信号

## 必看维度

- 题材和细分赛道
- 书名结构
- 简介前两句卖点
- 开篇三章的钩子类型
- 主角人设和关系引擎
- 平台偏好的节奏密度
- 长短篇不同的兑现速度

## 输出要求

至少输出以下内容：

- 当前平台的高频题材信号
- 3-5 个值得验证的机会方向
- 每个方向的卖点、门槛、风险
- 更适合长篇还是短篇
- 推荐转交给 `novel-ideation` 或 `novel-commercial-writing` 的下一步

优先按 `references/scan-output-spec.md` 的结构落盘。若当前是小说项目工作区，默认写入：

- `05-market/trend-notes.md`
- `05-market/benchmark-list.md`

如需参照完成态，读取：

- `assets/examples/trend-notes-example.md`
- `assets/examples/platform-comparison-example.md`

## 边界

- 不因为单本排名高就断言趋势成立
- 不只说“什么火”，还要说“为什么火”和“你是否适合写”
- 如果用户已经有题材，优先做验证而不是重做全榜概览

## 资源

- 平台差异：`references/platforms.md`
- 长短篇差异：`references/form-matrix.md`
- 题材分析维度：`references/genre-lenses.md`
- 输出模板：`references/scan-output-spec.md`
