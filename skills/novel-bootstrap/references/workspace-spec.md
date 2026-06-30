# 小说工作区规格

统一小说工程采用以下目录：

```text
00-story-core/
10-bible/
20-outline/
30-draft/
40-revision/
90-ops/
```

## 目录职责

- `00-story-core/`: 创作简报、作品定位、系列承诺
- `10-bible/`: hard canon、世界规则、人物与势力
- `20-outline/`: 主线结构、分卷计划、章节节拍卡、埋线与回收表
- `30-draft/`: 正文章节、场景和导入稿
- `40-revision/`: 体检报告、修订记录与章节报告
- `90-ops/`: 当前状态、决策、交接和连续性问题

## 最小可用状态

一个“能继续写”的项目至少应当有：

- `00-story-core/project-meta.md`
- `00-story-core/creative-brief.md`
- `20-outline/master-outline.md`
- `90-ops/current-state.md`

如果是中文长篇，建议再补：

- `20-outline/volumes/volume-01.md`
- `20-outline/chapter-beats/chapter-001.md`
- `20-outline/因果/scene-causality-map.md`
- `20-outline/payoff-tracking/payoff-ledger.md`
- `40-revision/checkup-reports/`

如果目标是“尽快进入长篇连载”，建议把下面这些当成快启核心：

- `00-story-core/creative-brief.md`
- `00-story-core/series-promise.md`
- `20-outline/volumes/volume-01.md`
- `20-outline/chapter-beats/chapter-001.md`
- `20-outline/first-arc-launchpad.md`
- `90-ops/current-state.md`
- `90-ops/serial-dashboard.md`

这套组合的目标不是一次把全书想完，而是先让作者能稳定写出前三章、第一卷和第一波追读点。
