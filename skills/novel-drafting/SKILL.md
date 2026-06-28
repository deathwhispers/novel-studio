---
name: novel-drafting
description: "中文小说正文起草 skill。用于根据现有设定和章节 beats 写场景、写章节、续写正文、补桥段，并在写完后回写当前状态和连续性信息。适用于“写下一章”“把这一章扩成正文”“先写这个场景”“按大纲继续往下写”等场景。"
---

# Novel Drafting

## Overview

按最小上下文包稳定产出正文，避免长篇写作时把整库资料一次性塞进上下文。正式起草前，先用写前自检锁定目标、阻力、因果、细节载体和章节尾推进器。写作完成后，要把状态回写到项目文件里；写长篇和写短篇时，节奏目标不能混用。

## 最小上下文包

默认只加载：

1. `00-story-core/project-meta.md`
2. `00-story-core/creative-brief.md`
3. 当前章节 beat
4. 当前卷文件

按需追加，而不是默认全读：

- 相关角色文件
- 相关 canon 条目
- 上一章正文
- `90-ops/current-state.md`
- 相关拆文分析中的 `Logic And Causality`
- 相关拆文分析中的 `Detail Carriers`
- 相关拆文分析中的 `Adaptation Notes For My Project`

如果是短篇，再优先读：

- `05-market/trend-notes.md`
- 目标短篇对标的拆文结果

如果是长篇，再优先读：

- `20-outline/causality/scene-causality-map.md`
- `20-outline/payoff-tracking/payoff-ledger.md`

在上下文包选完后，最后读取 `references/prewrite-checklist.md`，把空项补到“可以下笔”的程度再起草。

## 写前锁定

起草前至少明确：

1. 这章或这场到底要完成什么戏剧功能
2. 这一段是被什么前情结果逼出来的
3. 角色这次要主动做什么，以及会撞上什么阻力
4. 准备用哪些具体细节承载信息和情绪，而不是写到一半全靠抽象解释
5. 结尾要留下什么继续阅读的推动力

如果以上有三项以上说不清，先回到 `novel-outlining` 或连续性文件补齐，不要硬写。

## 场景级写作循环

每场至少要完成：

1. objective
2. friction
3. shift
4. aftermath

如果参考了拆文结果，再额外自检：

5. 这场的因果是否闭合
6. 这场用了什么具体细节承载信息或情绪

章节结束时保留明确的推动力，不要只是平静收束。

短篇场景则优先保证每场都在逼近题眼或结局效果，不追求长篇式层层留钩。

## 回写要求

写完正文后至少更新：

- `30-draft/chapters/` 中对应章节
- `90-ops/current-state.md` 中的当前进度、未决问题、下一步
- 如出现新 hard canon，补到 `10-bible/canon.md` 或记入 `90-ops/decisions.md`
- 如本章推进了伏笔或因果债，联动更新 `20-outline/causality/scene-causality-map.md` 或 `20-outline/payoff-tracking/payoff-ledger.md`

## 不在这里完成的事

- 不在 drafting 阶段大规模重构整本书结构
- 不在 drafting 阶段做精修级润色
- 如果发现大纲失效，转回 `novel-outlining`
- 如果发现成稿需要重点修订，转到 `novel-revision`
- 如果只是去 AI 味，不在这里硬修，转到 `novel-deslop`

需要更细的加载规则时，读取 `references/context-pack.md`；需要具体写前检查项时，读取 `references/prewrite-checklist.md`。
