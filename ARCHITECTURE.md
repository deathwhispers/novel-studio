# Architecture

这个仓库把“AI 写小说 skill”视为一个小型产品，而不是一个单文件 prompt。

## 设计原则

1. 单一职责

每个 skill 只承担一个阶段性的核心任务：

- `novel-market-scan` 负责市场研究
- `novel-deconstruction` 负责拆文
- `novel-bootstrap` 负责项目落地
- `novel-commercial-writing` 负责商业化改造
- `novel-deslop` 负责去 AI 味
- `novel-ideation` 负责创意收敛
- `novel-worldbuilding` 负责设定圣经
- `novel-outlining` 负责结构规划
- `novel-drafting` 负责正文起草
- `novel-revision` 负责修订和质检

`novel-studio` 只做路由，不抢子 skill 的工作。

2. 先有工程，再有对话

小说创作不是一次性回答，而是持续累积的工程。因此优先设计稳定的项目文件结构，再让 skill 围绕这些文件工作。

3. 最小上下文包

长篇写作最容易失控的地方不是“不会写”，而是“读太多上下文仍然抓不住关键”。所以正文写作明确要求最小上下文加载，而不是每次都把整个项目读一遍。

4. 硬资料和软资料分离

- `05-market/` 放平台研究、对标和拆文沉淀
- `10-bible/` 放硬设定与可追溯 canon
- `20-outline/` 放结构和剧情承诺
- `30-draft/` 放正文和场景
- `40-revision/` 放修订报告
- `90-ops/` 放当前状态、交接和决策日志

这样可以降低“正文、设定、工作记录混写”的混乱度。

## 从参考项目中吸收什么

### `awesome-novel-skill`

吸收点：

- 明确的角色分工
- 设定、记忆、模板的全面性

改进点：

- 把“多 agent + 多知识文件”进一步收敛成 skill 套件，不把所有流程挤进一个入口。
- 用统一项目模板替代大量风格各异的项目落地方式。

### `novel-creator-skill`

吸收点：

- 长篇一致性意识
- 长期记忆与测试意识

改进点：

- 将“脚本化流水线”与“Codex skill 可触发性”分开，避免系统过重。
- 不强依赖复杂自动流水线，先把基础 artifact 结构打稳。

### `chinese-novelist-skill`

吸收点：

- 清晰的阶段式流程
- 章节质量校验思路

改进点：

- 把流程拆成多个 skill，而不是把所有阶段固化在单一指令里。
- 从“阶段问答”升级为“阶段 + 文件产物”双驱动。

### `oh-story-claudecode`

吸收点：

- 主入口路由器思路
- 专项 skill 化

改进点：

- 让 skill 与小说项目模板深度绑定，而不只是命令分流。
- 更强调长篇项目的持续维护，而不是偏工具箱式集合。

## 推荐的小说项目结构

```text
my-novel/
├── 00-story-core/
│   ├── project-meta.md
│   ├── creative-brief.md
│   └── series-promise.md
├── 05-market/
│   ├── trend-notes.md
│   ├── benchmark-list.md
│   └── deconstructions/
├── 10-bible/
│   ├── canon.md
│   ├── world-rules.md
│   ├── locations.md
│   ├── factions.md
│   ├── timeline.md
│   ├── motifs.md
│   └── characters/
├── 20-outline/
│   ├── master-outline.md
│   ├── arc-tracker.md
│   ├── volumes/
│   └── chapter-beats/
├── 30-draft/
│   ├── chapters/
│   ├── scenes/
│   └── imported/
├── 40-revision/
│   ├── revision-log.md
│   └── chapter-reports/
└── 90-ops/
    ├── current-state.md
    ├── decisions.md
    ├── continuity-queries.md
    └── session-handoff.md
```

## 目录为何这样分层

### `00-story-core`

放作品最核心的目标与承诺。这里回答“这本书为什么存在”。

### `05-market`

放市场与对标研究。这里回答“什么值得写、哪些作品值得学、学什么而不是抄什么”。

### `10-bible`

放 hard canon 和高频检索资料。这里回答“这本书的世界是什么样、谁在里面行动”。

### `20-outline`

放结构承诺。这里回答“故事准备如何推进，哪些伏笔要回收”。

### `30-draft`

放真正的正文资产。这里回答“这一章或这一场到底写了什么”。

### `40-revision`

放修订痕迹和质量报告。这里回答“为了变好，这一稿改了什么”。

### `90-ops`

放运行态信息。这里回答“下次继续时先看哪里、卡在哪里、做过哪些关键决定”。

## skill 与文件的对应关系

| Skill | 主要读写区域 |
| --- | --- |
| `novel-market-scan` | `05-market/` |
| `novel-deconstruction` | `05-market/deconstructions/`, `05-market/benchmark-list.md` |
| `novel-bootstrap` | 全项目，尤其是模板初始化和导入 |
| `novel-commercial-writing` | `00-story-core/`, `05-market/`, `20-outline/`, `30-draft/` |
| `novel-deslop` | `30-draft/`, `40-revision/` |
| `novel-ideation` | `00-story-core/` |
| `novel-worldbuilding` | `10-bible/`, `90-ops/decisions.md` |
| `novel-outlining` | `20-outline/` |
| `novel-drafting` | `20-outline/`, `30-draft/`, `90-ops/current-state.md` |
| `novel-revision` | `30-draft/`, `40-revision/`, `90-ops/decisions.md` |

## 迭代建议

下一步最值得继续补强的部分：

1. 为 `novel-bootstrap` 增加“导入旧稿 -> 自动映射到模板”的半自动脚本。
2. 为 `novel-market-scan` 增加半自动榜单采样脚本或采样模板。
3. 为 `novel-drafting` 增加“根据 chapter beat 自动组装上下文包”的辅助脚本。
4. 为 `novel-revision` 和 `novel-deslop` 增加更细的章节修订报告模板。
5. 增加真实 forward-test 样例，验证 skill 在扫榜、拆文、开书、续写、改稿几种场景下的表现。
