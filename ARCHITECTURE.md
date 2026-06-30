# 项目架构

这个仓库把“AI 写小说 skill”视为一个小型产品，而不是一个单文件 prompt。

## 设计原则

1. 单一职责，但流程按中文写作习惯组织

每个 skill 只承担一个阶段性的核心任务：

- `novel-market-scan` 负责市场研究
- `novel-deconstruction` 负责拆文
- `novel-bootstrap` 负责项目落地
- `novel-commercial-writing` 负责商业化改造
- `novel-deslop` 负责去 AI 味
- `novel-ideation` 负责创意收敛
- `novel-worldbuilding` 负责设定圣经
- `novel-outlining` 负责结构规划
- `novel-checkup` 负责章节体检、卷级节奏体检、长线漏线扫描和追读弱点排查
- `novel-drafting` 负责正文起草
- `novel-revision` 负责修订和质检

`novel-studio` 只做路由，不抢子 skill 的工作。

2. 先有工作台，再有对话

小说创作不是一次性回答，而是持续累积的工程。因此优先设计稳定的项目文件结构，再让 skill 围绕这些文件工作。

3. 最小上下文包

长篇写作最容易失控的地方不是“不会写”，而是“读太多上下文仍然抓不住关键”。所以正文写作明确要求最小上下文加载，而不是每次都把整个项目读一遍。

对于长篇网文，项目初始化也遵循同样原则：先把“能开写”的必要文件搭起来，而不是第一天就把整套世界圣经写满。因此 `novel-bootstrap` 现在额外提供首卷快启卡、连载驾驶舱和连载章快启卡，优先服务“先把前三章和第一卷打顺”的目标。

`novel-drafting` 也沿用这个原则：先锁本章最重要的戏、最值钱的读点和最不能丢的旧线，再开始正文起草。它现在不只是“根据大纲续写”，而是带有写前卡、质量标准、续写防漂卡和写后自检卡的一整套正文质量控制层。

4. 硬资料、正文、体检、运行记录分离

- `05-market/` 放平台研究、对标和拆文沉淀
- `10-bible/` 放硬设定与可追溯 canon
- `20-outline/` 放结构和剧情承诺
- `30-draft/` 放正文和场景
- `40-revision/` 放体检报告和修订报告
- `90-ops/` 放当前状态、交接和决策日志

这样可以降低“正文、设定、工作记录混写”的混乱度。

5. 先体检，再重修

中文小说写作里，“写完先顺逻辑和照应，再谈润色”比一步到位更稳。所以流程里显式加入 `novel-checkup`，把“前后打架没有、漏线没有、人物状态是否续上、章尾发动机是否还在、卷节奏有没有塌、最近为什么不够想追了”先查一遍，再进入 `novel-revision`。

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

## 推荐的小说工作台结构

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
│   ├── first-arc-launchpad.md
│   ├── volumes/
│   └── chapter-beats/
├── 30-draft/
│   ├── chapters/
│   ├── scenes/
│   └── imported/
├── 40-revision/
│   ├── revision-log.md
│   ├── checkup-reports/
│   └── chapter-reports/
└── 90-ops/
    ├── current-state.md
    ├── serial-dashboard.md
    ├── decisions.md
    ├── continuity-queries.md
    └── session-handoff.md
```

## 目录为何这样分层

### `00-story-core`

放作品最核心的目标与承诺。这里回答“这本书到底卖什么、为什么值得读”。

### `05-market`

放市场与对标研究。这里回答“什么值得写、哪些作品值得学、学什么而不是抄什么”。

### `10-bible`

放 hard canon 和高频检索资料。这里回答“这本书的世界是什么样、谁在里面行动”。

### `20-outline`

放结构承诺。这里回答“故事准备如何推进，哪些线什么时候要碰、要收”。

如果是长篇网文快启，`20-outline/first-arc-launchpad.md` 用来先锁第一卷和前三章，不要求立即想完整本书。

### `30-draft`

放真正的正文资产。这里回答“这一章或这一场到底写了什么”。

这里不只存正文，也承接“如何更稳地把正文写出来”的工作文件，包括写前卡、连载快启卡和场景拆写草稿。

### `40-revision`

放体检痕迹和修订报告。这里回答“这一章哪里有病、怎么修、修完还剩什么风险”。

这里不仅放章节体检，也放卷体检、长线漏线扫描和追读弱点排查。

### `90-ops`

放运行态信息。这里回答“下次继续时先看哪里、卡在哪里、做过哪些关键决定”。

如果已经进入连载，`90-ops/serial-dashboard.md` 应作为高频回看的驾驶舱，而不是把这些运行信息散落在多个文档里。

## 推荐流程链

默认主链路：

`novel-bootstrap -> novel-ideation -> novel-worldbuilding -> novel-outlining -> novel-drafting -> novel-checkup -> novel-revision`

按需外挂：

- 题材和平台还没定稳时，先走 `novel-market-scan -> novel-deconstruction`
- 想强化平台适配和留存时，补 `novel-commercial-writing`
- 主要问题是模板感和解释腔时，补 `novel-deslop`

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
| `novel-checkup` | `20-outline/`, `30-draft/`, `40-revision/checkup-reports/`, `90-ops/current-state.md`, `90-ops/serial-dashboard.md` |
| `novel-drafting` | `20-outline/`, `30-draft/`, `90-ops/current-state.md`, `90-ops/serial-dashboard.md` |
| `novel-revision` | `30-draft/`, `40-revision/`, `90-ops/decisions.md` |

## 迭代建议

下一步最值得继续补强的部分：

1. 为 `novel-bootstrap` 增加“导入旧稿 -> 自动映射到模板”的半自动脚本。
2. 为 `novel-market-scan` 增加半自动榜单采样脚本或采样模板。
3. 为 `novel-drafting` 增加“根据 chapter beat 自动组装上下文包”的辅助脚本。
4. 为 `novel-checkup` 增加更细的 forward-test，验证卷体检、漏线扫描和追读排查在真实任务中是否足够稳。
5. 增加真实 forward-test 样例，验证 skill 在扫榜、拆文、开书、续写、体检、改稿几种场景下的表现。
