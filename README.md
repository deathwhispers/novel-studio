# novel-skills

面向中文小说创作的 Codex skill 套件。它不是一个巨大的单体提示词，而是一组能协同工作的专项 skill，加上一套可直接落地的小说工程模板，覆盖扫榜、拆文、长短篇写作、商业化改造和去 AI 味。

## 目标

- 把“扫榜、拆文、开书、设定、列纲、写作、商业化、去 AI 味”拆成独立能力，避免一个 skill 过度臃肿。
- 让长篇创作依赖稳定的项目结构，而不是把全部记忆都塞进单次对话。
- 同时兼顾长篇、短篇与不同平台/题材的适配差异。
- 让 skill 本身可维护、可验证、可扩展，而不是只在某一次演示里有效。

## 仓库结构

```text
novel-skills/
├── ARCHITECTURE.md
├── README.md
├── scripts/
│   └── validate_skills.py
└── skills/
    ├── novel-studio/
    ├── novel-market-scan/
    ├── novel-deconstruction/
    ├── novel-bootstrap/
    ├── novel-commercial-writing/
    ├── novel-deslop/
    ├── novel-ideation/
    ├── novel-worldbuilding/
    ├── novel-outlining/
    ├── novel-drafting/
    └── novel-revision/
```

## Skills

| Skill | 职责 |
| --- | --- |
| `novel-studio` | 总控路由，根据用户意图和工作区状态分流 |
| `novel-market-scan` | 扫榜、看平台差异、判断题材和长短篇机会 |
| `novel-deconstruction` | 拆解爆款、样章和对标作品，提炼可迁移技法 |
| `novel-bootstrap` | 初始化小说项目、导入旧稿、迁移现有资料 |
| `novel-commercial-writing` | 做书名、简介、钩子、留存和平台适配优化 |
| `novel-deslop` | 专做去 AI 味，修正模板感与解释腔 |
| `novel-ideation` | 从模糊点子收敛为创作简报和读者承诺 |
| `novel-worldbuilding` | 构建人物、世界规则、设定圣经和连续性 |
| `novel-outlining` | 生成主线、分卷、章节 beats 和回收计划 |
| `novel-drafting` | 按最小上下文包写场景或章节，并回写状态 |
| `novel-revision` | 做结构修订、连贯性修复、文风校准和去 AI 味 |

## 为什么比参考项目更进一步

- 不把“小说创作”做成单一超级 skill，而是显式分成多个可组合能力。
- 把“市场研究 -> 对标拆解 -> 商业化改造 -> 实际写作”接成一条链，而不只关注正文生成。
- 项目模板按创作阶段分层，适合长期维护，而不是单纯堆积笔记文件。
- `novel-drafting` 明确了最小上下文包，减少长篇写作时的提示词膨胀。
- `novel-drafting` 现在自带写前自检，先锁目标、阻力、因果、细节和章节尾推进器，再下笔。
- `novel-bootstrap` 自带模板资产和初始化脚本，能直接落地成项目。
- 提供 `validate_skills.py`，方便批量校验 skill 结构。
- `novel-market-scan` 和 `novel-deconstruction` 现在都带标准输出模板与完成态样例，降低实际使用门槛。
- `novel-revision` 现在按逻辑修复、细节修复、伏笔回收修复三类模板组织，更适合做有针对性的成稿修订。

## 快速开始

1. 初始化一个新的小说工程：

```bash
python3 skills/novel-bootstrap/scripts/init_novel_project.py \
  --output /path/to/my-novel \
  --title "书名" \
  --genre "奇幻" \
  --premise "一句话故事前提"
```

2. 校验全部 skill：

```bash
python3 scripts/validate_skills.py
```

3. 如果要把这个仓库作为 Codex plugin 安装：

```bash
python3 scripts/install_codex_plugin.py
```

安装后重启 Codex，并新开一个 thread 再测试。

4. 在 Codex 中按任务调用：

- 不确定该用哪个 skill：`$novel-studio`
- 想先看什么题材和平台更有机会：`$novel-market-scan`
- 想拆一本爆款或样章：`$novel-deconstruction`
- 想从零开书：`$novel-bootstrap` -> `$novel-ideation`
- 想把选题做得更商业化：`$novel-commercial-writing`
- 已有设定，准备列纲：`$novel-outlining`
- 已有纲和设定，准备写正文：`$novel-drafting`
- 想专门去 AI 味：`$novel-deslop`
- 想做重写或结构修订：`$novel-revision`

## 安装为 Codex Plugin

这个仓库现在已经补齐了 Codex plugin 的基础结构：

- 插件 manifest：[`/.codex-plugin/plugin.json`](/Users/whisper/IdeaProjects/github/novel-skills/.codex-plugin/plugin.json)
- 本地 marketplace：[`/.agents/plugins/marketplace.json`](/Users/whisper/IdeaProjects/github/novel-skills/.agents/plugins/marketplace.json)
- 一键安装脚本：[`scripts/install_codex_plugin.py`](/Users/whisper/IdeaProjects/github/novel-skills/scripts/install_codex_plugin.py)
- 卸载脚本：[`scripts/uninstall_codex_plugin.py`](/Users/whisper/IdeaProjects/github/novel-skills/scripts/uninstall_codex_plugin.py)
- 打包脚本：[`scripts/build_plugin_bundle.sh`](/Users/whisper/IdeaProjects/github/novel-skills/scripts/build_plugin_bundle.sh)

本地开发安装：

```bash
python3 scripts/install_codex_plugin.py
```

如果只想重新刷新 marketplace，而不重复注册：

```bash
python3 scripts/install_codex_plugin.py --skip-marketplace-add
```

如果你想生成一个可分发的本地 bundle：

```bash
bash scripts/build_plugin_bundle.sh
```

它会输出一个 zip 包，解压后执行其中的 `python3 install_codex_plugin.py` 即可安装。

## 扫榜与拆文落盘

现在这两个环节已经有统一模板，不需要用户自己想格式：

- 扫榜优先落到 `05-market/trend-notes.md` 和 `05-market/benchmark-list.md`
- 拆文优先落到 `05-market/deconstructions/{对标名}-analysis.md`

可直接参考的样例：

- [trend-notes-example.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-market-scan/assets/examples/trend-notes-example.md)
- [platform-comparison-example.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-market-scan/assets/examples/platform-comparison-example.md)
- [benchmark-analysis-example.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-deconstruction/assets/examples/benchmark-analysis-example.md)
- [golden-hook-example.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-deconstruction/assets/examples/golden-hook-example.md)
- [retention-analysis-example.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-deconstruction/assets/examples/long-form/retention-analysis-example.md)
- [compression-analysis-example.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-deconstruction/assets/examples/short-form/compression-analysis-example.md)

## 拆文如何反哺写作

现在拆文结果不再只是分析层，而是会直接服务写作质量：

- `novel-drafting` 会优先继承拆文里的 `Logic And Causality`、`Detail Carriers` 和 `Adaptation Notes For My Project`
- `novel-outlining` 会同步维护 `20-outline/causality/scene-causality-map.md`
- `novel-outlining` 会同步维护 `20-outline/payoff-tracking/payoff-ledger.md`

这两张表的模板参考：

- [causality-map-template.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-outlining/references/causality-map-template.md)
- [payoff-ledger-template.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-outlining/references/payoff-ledger-template.md)

## 质量强化工作流

现在写作和修订的质量控制也有固定落点：

- 起草前先用 [prewrite-checklist.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-drafting/references/prewrite-checklist.md) 锁定章节目标、阻力、因果、细节载体和结尾推进器。
- 初始化项目后，可直接在 [chapter-prewrite-checklist.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-bootstrap/assets/novel-project-template/30-draft/prewrite/chapter-prewrite-checklist.md) 基础上复制填写。
- 修订时按问题类型进入 [logic-repair-template.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-revision/references/logic-repair-template.md)、[detail-repair-template.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-revision/references/detail-repair-template.md) 或 [payoff-repair-template.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-revision/references/payoff-repair-template.md)。
- 小说工程模板里也同步放好了三份 chapter report 模板，便于长期追踪每章修过什么、还剩什么风险。

## 参考来源

这个仓库吸收了以下项目的优点，并在结构化、可维护性和项目模板层面继续前推：

- [modoojunko/awesome-novel-skill](https://github.com/modoojunko/awesome-novel-skill)
- [leenbj/novel-creator-skill](https://github.com/leenbj/novel-creator-skill)
- [PenglongHuang/chinese-novelist-skill](https://github.com/PenglongHuang/chinese-novelist-skill)
- [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)

更细的设计 rationale 见 `ARCHITECTURE.md`。
