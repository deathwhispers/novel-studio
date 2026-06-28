---
name: novel-studio
description: "中文小说工作台路由 skill。用于用户想写小说但任务还不够明确，或需要在开书、导入旧稿、补设定、列大纲、写章节、重写润色之间自动分流时。检查当前工作区是否已有 `00-story-core/`, `10-bible/`, `20-outline/`, `30-draft/` 等小说工程文件，再把任务路由到 `novel-bootstrap`、`novel-ideation`、`novel-worldbuilding`、`novel-outlining`、`novel-drafting` 或 `novel-revision`。"
---

# Novel Studio

## Overview

只做路由，不直接承担整本小说的完整产出。先判断用户到底处在“看市场、拆对标、开书、补设定、列纲、写作、商业化优化、去 AI 味”中的哪一步，再调用最合适的子 skill。

## 路由顺序

按以下顺序判断，匹配到第一项后就停止继续分流：

1. 用户想知道什么题材火、哪个平台适合、长短篇怎么选
   - 路由到 `novel-market-scan`
2. 用户想拆解爆款、分析样章、研究对标书
   - 路由到 `novel-deconstruction`
3. 用户想做书名、简介、开篇、追读、平台适配或商业化改造
   - 路由到 `novel-commercial-writing`
4. 用户重点是去 AI 味、改自然、改人味节奏
   - 路由到 `novel-deslop`
5. 工作区里不存在 `00-story-core/project-meta.md`
   - 路由到 `novel-bootstrap`
6. 用户只有点子、题材、角色火花，尚未形成清晰故事承诺
   - 路由到 `novel-ideation`
7. 用户重点在人物、势力、设定、时间线、世界规则或连续性
   - 路由到 `novel-worldbuilding`
8. 用户重点在主线、分卷、幕结构、章节 beats、伏笔回收
   - 路由到 `novel-outlining`
9. 用户已经有设定和章节计划，想写下一章、下一场或续写正文
   - 路由到 `novel-drafting`
10. 用户已经有正文，想重写、查错、润色、修结构
   - 路由到 `novel-revision`

## 路由规则

- 优先看用户的当前意图，不要因为工作区里有旧文件就忽略用户新需求。
- 如果一个请求同时跨多个阶段，按链路顺序拆开处理。
  - 例如“先扫榜再帮我做一本能卖的玄幻书”，先 `novel-market-scan`，再 `novel-commercial-writing`，最后转 `novel-ideation`。
- 最多只为路由追问一个窄问题。
  - 例如“你现在是想先看市场，还是已经有题材要直接开书？”
- 不在路由层写整章正文，不在路由层做深度拆文，也不在路由层做大段去味。

## 工作区信号

优先检查以下文件信号：

- `00-story-core/project-meta.md`
- `00-story-core/creative-brief.md`
- `05-market/trend-notes.md`
- `05-market/benchmark-list.md`
- `05-market/deconstructions/`
- `10-bible/canon.md`
- `20-outline/master-outline.md`
- `20-outline/chapter-beats/`
- `30-draft/chapters/`
- `40-revision/chapter-reports/`
- `90-ops/current-state.md`

如果需要更细的路由例子，读取 `references/routing-map.md`。

## 输出要求

- 明确说出准备转到哪个 skill。
- 如果需要多步，给出最短的下一步链路。
- 保持简洁，不展开实现细节。
