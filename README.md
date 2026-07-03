# novel-skills

面向中文小说创作的 **多 AI 工具兼容 skill 套件**。它不是一个巨大的单体提示词，而是一组能协同工作的专项 skill，加上一套可直接落地的小说工作台模板，覆盖扫榜、拆书、立项、设定、铺线、写章、体检、重修、商业化改稿和去 AI 味。

## 支持的工具

本项目支持 3 种主流 AI 编程工具的便捷部署：

- **Codex CLI**（OpenAI）
- **Claude Code**（Anthropic）
- **OpenCode**（开源）

统一的 `python3 scripts/install.py` 会自动检测已安装的工具并安装。详细见 [DEPLOYMENT.md](DEPLOYMENT.md)。

## 目标

- 把“扫榜、拆文、开书、设定、列纲、写作、商业化、去 AI 味”拆成独立能力，避免一个 skill 过度臃肿。
- 让长篇创作依赖稳定的项目结构，而不是把全部记忆都塞进单次对话。
- 同时兼顾长篇、短篇与不同平台/题材的适配差异。
- 让 skill 本身可维护、可验证、可扩展，而不是只在某一次演示里有效。

## 设计原则

1. 单一职责，但流程按中文写作习惯组织。每个 skill 只承担一个阶段性的核心任务，novel-studio 只做路由，不抢子 skill 的工作。

2. 先有工作台，再有对话。小说创作不是一次性回答，而是持续累积的工程，因此优先设计稳定的项目文件结构，再让 skill 围绕这些文件工作。

3. 最小上下文包。长篇写作最容易失控的不是不会写，而是读太多上下文仍然抓不住关键。正文写作和项目初始化都遵循这个原则——先把能开写的必要文件搭起来，而不是第一天就把整套世界圣经写满。

4. 硬资料、正文、体检、运行记录分离。10-设定/、30-正文/、40-修订/、90-运行/ 各司其职，降低正文、设定、工作记录混写的混乱度。

5. 先体检，再重修。写完先查前后照应、漏线、人物状态、章尾发动机和卷节奏，再进 novel-revision 做针对性修订。

## 仓库结构

```text
novel-skills/
├── README.md                # 本文件
├── DEPLOYMENT.md            # 多工具部署指南
├── scripts/
│   ├── install.py           # 统一安装脚本（Codex/Claude/OpenCode）
│   ├── uninstall.py         # 统一卸载脚本
│   ├── install_codex_plugin.py  # 旧版 Codex 安装脚本（保留兼容）
│   ├── validate_skills.py   # skill 校验
│   ├── validate_novel_project.py  # 项目结构校验
│   ├── extract_index.py     # 前文索引抽取
│   ├── create_chapter.py    # 创建章节文件
│   ├── evaluate_chapter.py  # 章节评估
│   ├── export_novel.py      # 导出
│   └── build_plugin_bundle.sh  # 构建插件包
├── .codex-plugin/           # Codex 专用配置
│   └── plugin.json
├── .claude-plugin/          # Claude Code 专用配置
│   ├── plugin.json
│   ├── marketplace.json
│   └── commands/            # 斜杠命令
├── .opencode/               # OpenCode 专用配置
│   ├── commands/
│   └── agents/
├── opencode.json            # OpenCode 插件清单
├── .agents/                 # Codex marketplace 配置
│   └── plugins/marketplace.json
└── skills/                  # 14 个 skill 套件
    ├── novel-studio/
    ├── novel-market-scan/
    ├── novel-deconstruction/
    ├── novel-bootstrap/
    ├── novel-commercial-writing/
    ├── novel-deslop/
    ├── novel-ideation/
    ├── novel-worldbuilding/
    ├── novel-outlining/
    ├── novel-checkup/
    ├── novel-drafting/
    ├── novel-revision/
    ├── novel-volumning/
    └── novel-ai-writing/
```

## 中文技能名

| 目录名 | 对外名称 | 职责 |
| --- | --- | --- |
| `novel-studio` | 小说工作台 | 总控路由，根据用户意图和工作区状态分流 |
| `novel-market-scan` | 扫榜看盘 | 扫榜、看平台差异、判断题材和长短篇机会 |
| `novel-deconstruction` | 拆书拆章 | 拆解爆款、样章和对标作品，提炼可迁移技法 |
| `novel-bootstrap` | 开书建档 | 初始化小说项目、导入旧稿、迁移现有资料 |
| `novel-commercial-writing` | 商业化改稿 | 做书名、简介、钩子、留存和平台适配优化 |
| `novel-deslop` | 去 AI 味 | 专做去 AI 味，修正模板感与解释腔 |
| `novel-ideation` | 立项定核 | 从模糊点子收敛为创作简报和读者承诺 |
| `novel-worldbuilding` | 设定总表 | 构建人物、世界规则、设定圣经和连续性 |
| `novel-outlining` | 铺线列纲 | 生成主线、分卷、章节节拍卡和回收计划 |
| `novel-checkup` | 小说体检 | 检查单章、卷节奏、长线漏线、伏笔回收、连续性和追读弱点 |
| `novel-drafting` | 写章起稿 | 按最小上下文包写场景或章节，并回写状态 |
| `novel-revision` | 重修统稿 | 做结构修订、连贯性修复、文风校准和去 AI 味 |
| `novel-volumning` | 卷纲工坊 | 分卷卷纲逐卷建设和迭代 |
| `novel-ai-writing` | AI 协作写作 | 把所有写作能力转译成 AI prompt 模板（写前/写中/写后+特殊场景） |

## 为什么比参考项目更进一步

- 不把“小说创作”做成单一超级 skill，而是显式分成多个可组合能力。
- 把“市场研究 -> 对标拆解 -> 商业化改造 -> 实际写作”接成一条链，而不只关注正文生成。
- 项目模板按中文作者的真实工作链路分层，适合长期维护，而不是单纯堆积笔记文件。
- `novel-drafting` 明确了最小上下文包，减少长篇写作时的提示词膨胀。
- `novel-drafting` 现在自带写前自检，先锁目标、阻力、因果、细节和章节尾推进器，再下笔。
- `novel-drafting` 现在新增章节质量标准、长篇续写防漂卡和写后自检卡，更适合稳定产出长篇连载正文。
- 新增 `novel-checkup`，把“写完先体检再重修”的流程独立出来，更贴近中文长篇连载的实际习惯。
- `novel-checkup` 现在不只看单章，还会做卷体检、长线漏线扫描和追读弱点排查，更贴近长篇网文真正的核心风险。
- `novel-bootstrap` 自带模板资产和初始化脚本，能直接落地成项目。
- 提供 `validate_skills.py`，方便批量校验 skill 结构。
- `novel-market-scan` 和 `novel-deconstruction` 现在都带标准输出模板与完成态样例，降低实际使用门槛。
- `novel-revision` 现在按逻辑修复、细节修复、伏笔回收修复三类模板组织，更适合做有针对性的成稿修订。

## 从参考项目中吸收什么

### awesome-novel-skill

吸收：明确的角色分工，设定、记忆、模板的全面性。
改进：把多 agent + 多知识文件进一步收敛成 skill 套件，用统一项目模板替代大量风格各异的项目落地方式。

### novel-creator-skill

吸收：长篇一致性意识，长期记忆与测试意识。
改进：将脚本化流水线与 Codex skill 可触发性分开，不强依赖复杂自动流水线，先把基础 artifact 结构打稳。

### chinese-novelist-skill

吸收：清晰的阶段式流程，章节质量校验思路。
改进：把流程拆成多个 skill，从阶段问答升级为「阶段 + 文件产物」双驱动。

### oh-story-claudecode

吸收：主入口路由器思路，专项 skill 化。
改进：让 skill 与小说项目模板深度绑定，更强调长篇项目的持续维护。

## 推荐工作流

更贴近中文作者习惯的顺序是：

`开书建档 -> 立项定核 -> 设定总表 -> 铺线列纲 -> 写章起稿 -> 小说体检 -> 重修统稿 -> 去 AI 味 / 商业化改稿`

如果题材、平台和卖点还没想清，可以把 `扫榜看盘 -> 拆书拆章` 放在前面，先做选题判断和对标吸收。

## 项目工作台结构

初始化后的项目遵循以下目录分层：

```
my-novel/
├── 00-书核/          # 核心目标与承诺：这本书卖什么、为什么值得读
├── 05-市场/          # 市场与对标研究：什么值得写、哪些作品值得学
├── 10-设定/          # hard canon 和高频检索：世界观、角色、规则
├── 20-大纲/          # 结构承诺：故事如何推进，哪些线何时碰、何时收
├── 30-正文/          # 正文资产：每章每场到底写了什么
├── 40-修订/          # 体检痕迹和修稿报告：哪里有病、怎么修、剩什么风险
├── 50-归档/          # 已完成的分卷和旧版大纲
└── 90-运行/          # 运行态信息：当前进度、连载驾驶舱、决策记录
```

这套分层的核心逻辑：

- **00-书核**：回答「这本书到底卖什么、为什么值得读」
- **05-市场**：回答「什么值得写、哪些作品值得学、学什么而不是抄什么」
- **10-设定**：回答「这本书的世界是什么样、谁在里面行动」
- **20-大纲**：回答「故事准备如何推进，哪些线什么时候要碰、要收」
- **30-正文**：回答「这一章或这一场到底写了什么」，也承接写前卡、连载快启和场景草稿
- **40-修订**：回答「这一章哪里有病、怎么修、修完还剩什么风险」
- **90-运行**：回答「下次继续时先看哪里、卡在哪里、做过哪些关键决定」

## 快速开始

1. 初始化一个新的小说工程：

```bash
python3 skills/novel-bootstrap/scripts/init_novel_project.py \
  --output /path/to/my-novel \
  --title "书名" \
  --genre "奇幻" \
  --premise "一句话故事前提"
```

如果目标是快速启动长篇网文，不要一上来把全书所有设定写满。初始化后优先补这些文件：

- `00-书核/立项单.md`
- `00-书核/长线承诺.md`
- `20-大纲/首卷发射台.md`
- `20-大纲/分卷/volume-01.md`
- `20-大纲/节拍卡/chapter-001.md`
- `90-运行/连载驾驶舱.md`

这套组合的目标是先把第一卷卖点、前三章钩子和连载驾驶舱搭起来，尽快进入可持续写稿状态。

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
- 已写完一章，先查前后照应和连续性：`$novel-checkup`
- 一卷写完了，或者最近几章追读变弱了：`$novel-checkup`
- 已有纲和设定，准备写正文：`$novel-drafting`
- 想专门去 AI 味：`$novel-deslop`
- 想做重写或结构修订：`$novel-revision`
- 想逐卷细化卷纲：`$novel-volumning`
- 想让 AI 帮我写一节对话/战斗/感情戏/批量生成：`$novel-ai-writing`

## 新手使用手册

如果你是第一次用这套工具，建议直接照下面这一条链路走，不要一上来同时开十几个文件。

### 第一步：初始化一个项目

执行：

```bash
python3 skills/novel-bootstrap/scripts/init_novel_project.py \
  --output /path/to/my-novel \
  --title "书名" \
  --genre "题材" \
  --premise "一句话故事前提"
```

初始化后，先只看这几个文件：

- `00-书核/作品总表.md`
- `00-书核/立项单.md`
- `20-大纲/首卷发射台.md`
- `20-大纲/分卷/volume-01.md`
- `20-大纲/节拍卡/chapter-001.md`
- `20-大纲/节拍卡/chapter-002.md`
- `20-大纲/节拍卡/chapter-003.md`
- `90-运行/连载驾驶舱.md`

### 第二步：先把书核和前三章锁住

建议按这个顺序填：

1. `00-书核/立项单.md`
2. `00-书核/长线承诺.md`
3. `20-大纲/首卷发射台.md`
4. `20-大纲/分卷/volume-01.md`
5. `20-大纲/节拍卡/chapter-001.md`
6. `20-大纲/节拍卡/chapter-002.md`
7. `20-大纲/节拍卡/chapter-003.md`

这一步的目标不是想完整本书，而是先回答：

- 这本书真正卖什么
- 第一卷主要卖什么
- 前三章各自要完成什么
- 第三章结束后，读者为什么会想继续追

### 第三步：在 Codex 里开第一轮对话

如果你只有模糊脑洞，先用：

```text
用 $novel-ideation 帮我把这个点子收成一本适合长篇连载的书核，并补齐创作简报。
```

如果你已经有书核，直接用：

```text
用 $novel-outlining 根据我的创作简报、首卷快启卡和第一卷卷纲，把前三章节拍卡铺出来。
```

### 第四步：写第一章正文

先确保这些文件已经至少有初稿：

- `00-书核/立项单.md`
- `20-大纲/分卷/volume-01.md`
- `20-大纲/节拍卡/chapter-001.md`
- `90-运行/当前进度.md`

然后在 Codex 里用：

```text
用 $novel-drafting 根据现有创作简报、第一卷卷纲、chapter-001 节拍卡和当前状态写第一章正文，并优先保证逻辑、细节和章尾推动力。
```

如果你在连载中续写下一章，可改用：

```text
用 $novel-drafting 根据现有大纲、serial-dashboard 和上一章状态写下一章，并先防止续写漂移。
```

### 第五步：写完后先体检，再修

第一章初稿出来后，不要立刻润色，先体检。

章节体检：

```text
用 $novel-checkup 帮我检查这一章的前后照应、人物状态、伏笔回收和章尾推动力，并输出一份问题清单。
```

如果是一卷写完，或者最近几章追读弱了：

```text
用 $novel-checkup 帮我做这一卷的卷体检，并排查最近几章的追读弱点。
```

再根据体检结果进入修订：

```text
用 $novel-revision 根据体检结果优先修这一章的逻辑、细节和回收问题。
```

### 第六步：每次写完都回写状态

至少更新这些文件：

- `30-正文/章节/` 对应章节
- `90-运行/当前进度.md`
- `90-运行/连载驾驶舱.md`
- 如有新伏笔或回收变化，再更新 `20-大纲/回收/payoff-ledger.md`
- 如有新因果推进，再更新 `20-大纲/因果/scene-causality-map.md`

### 一个最小可行用法

如果你现在只想尽快把第一章写出来，可以直接照这个最小顺序：

1. 初始化项目
2. 填 `立项单.md`
3. 填 `首卷发射台.md`
4. 填 `chapter-001.md`
5. 用 `$novel-drafting` 写第一章
6. 用 `$novel-checkup` 查问题
7. 用 `$novel-revision` 修第一章

## 安装到 AI 工具

本项目支持 3 种主流 AI 工具的便捷部署。**统一安装脚本会自动检测已安装的工具**：

```bash
python3 scripts/install.py
```

支持的工具：

| 工具 | 配置文件 | 安装路径 | 调用方式 |
|------|---------|---------|---------|
| **Codex CLI** (OpenAI) | `~/.codex/config.toml` | `~/.codex/plugins/cache/...` | `$novel-studio` |
| **Claude Code** (Anthropic) | `~/.claude/settings.json` | `~/.claude/plugins/novel-skills/` | `/novel` |
| **OpenCode** (开源) | `~/.config/opencode/config.json` | `~/.config/opencode/skills/...` | `/novel` |

### 快速安装

```bash
# 自动检测 + 提示选择
python3 scripts/install.py

# 指定工具
python3 scripts/install.py --target codex
python3 scripts/install.py --target claude
python3 scripts/install.py --target opencode

# 安装到所有已检测到的工具
python3 scripts/install.py --target all

# 仅复制 skills/ 目录（不安装为插件）
python3 scripts/install.py --skills-only --target-dir /path/to/project
```

### 卸载

```bash
python3 scripts/install.py --uninstall
# 或
python3 scripts/uninstall.py
```

详细部署文档（每种工具的细节、配置文件路径、故障排除）：[DEPLOYMENT.md](DEPLOYMENT.md)

### 兼容性

| 操作 | Codex | Claude Code | OpenCode |
|------|-------|-------------|----------|
| 安装到全局 | ✅ | ✅ | ✅ |
| 在项目内打开 | ❌ | ❌ | ✅ |
| 斜杠命令 | `$skill-name` | `/skill-name` | `/skill-name` |
| 角色扮演（agent） | ✅ | ✅ | ✅ |
| 卸载 | ✅ | ✅ | ✅ |

### 旧版 Codex 脚本（保留兼容）

```bash
# 旧版 Codex 安装脚本（仍可用）
python3 scripts/install_codex_plugin.py

# 旧版 Codex 卸载脚本（仍可用）
python3 scripts/uninstall_codex_plugin.py

# 打包成可分发的 bundle
bash scripts/build_plugin_bundle.sh
```

## 扫榜与拆文落盘

现在这两个环节已经有统一模板，不需要用户自己想格式：

- 扫榜优先落到 `05-市场/趋势笔记.md` 和 `05-市场/对标书单.md`
- 拆文优先落到 `05-市场/拆解/{对标名}-analysis.md`

可直接参考的样例：

- [趋势笔记样例.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-market-scan/assets/examples/趋势笔记样例.md)
- [平台对比样例.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-market-scan/assets/examples/平台对比样例.md)
- [对标分析样例.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-deconstruction/assets/examples/对标分析样例.md)
- [黄金钩样例.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-deconstruction/assets/examples/黄金钩样例.md)
- [留存分析样例.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-deconstruction/assets/examples/long-form/留存分析样例.md)
- [压缩分析样例.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-deconstruction/assets/examples/short-form/压缩分析样例.md)

## 拆文如何反哺写作

现在拆文结果不再只是分析层，而是会直接服务写作质量：

- `novel-drafting` 会优先继承拆文里的“因果怎么闭合”“细节抓手”“迁移到我项目里的注意点”
- `novel-outlining` 会同步维护 `20-大纲/因果/scene-causality-map.md`
- `novel-outlining` 会同步维护 `20-大纲/回收/payoff-ledger.md`

这两张表的模板参考：

- [因果图模板.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-outlining/references/因果图模板.md)
- [回收总账模板.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-outlining/references/回收总账模板.md)

## 质量强化工作流

现在写作和修订的质量控制也有固定落点：

- 起草前先用 [写前检查表.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-drafting/references/写前检查表.md) 锁定章节目标、阻力、因果、细节载体和结尾推进器。
- 起稿时可用 [章节质量标准.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-drafting/references/章节质量标准.md) 守住章节最低质量线，避免只把字数铺出来。
- 长篇续写前可用 [连载续写卡.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-drafting/references/连载续写卡.md) 先防漂，再下笔。
- 正文初稿写完后，先用 [写后自检卡.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-drafting/references/写后自检卡.md) 判断是继续写、先体检还是先修订。
- 做章节或卷体检时，可用 [章节体检模板.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-checkup/references/章节体检模板.md)、[卷体检模板.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-checkup/references/卷体检模板.md)、[长线扫描模板.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-checkup/references/长线扫描模板.md) 和 [追读排查.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-checkup/references/追读排查.md) 直接落报告。
- 初始化项目后，可直接在 [chapter-写前检查表.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-bootstrap/assets/novel-project-template/30-正文/写前/chapter-写前检查表.md) 基础上复制填写。
- 修订时按问题类型进入 [逻辑修补模板.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-revision/references/逻辑修补模板.md)、[细节修补模板.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-revision/references/细节修补模板.md) 或 [回收修补模板.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-revision/references/回收修补模板.md)。
- 小说工程模板里也同步放好了三份 chapter report 模板，便于长期追踪每章修过什么、还剩什么风险。

`novel-checkup` 现在也有真实样例报告，可以直接照着看判断方式和落报告方式：

- [章节体检样例.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-checkup/assets/examples/章节体检样例.md)
- [卷体检样例.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-checkup/assets/examples/卷体检样例.md)
- [长线扫描样例.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-checkup/assets/examples/长线扫描样例.md)
- [追读排查样例.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-checkup/assets/examples/追读排查样例.md)

如果正在日更或周更，可额外配合这些快启文件：

- [first-arc-launchpad.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-bootstrap/assets/novel-project-template/20-大纲/首卷发射台.md)
- [serial-dashboard.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-bootstrap/assets/novel-project-template/90-运行/连载驾驶舱.md)
- [serial-chapter-quickstart.md](/Users/whisper/IdeaProjects/github/novel-skills/skills/novel-bootstrap/assets/novel-project-template/30-正文/写前/serial-chapter-quickstart.md)

## Skill 与文件的对应关系

| Skill | 主要读写区域 |
| --- | --- |
| novel-market-scan | 05-市场/ |
| novel-deconstruction | 05-市场/拆解/, 05-市场/对标书单.md |
| novel-bootstrap | 全项目，尤其是模板初始化和导入 |
| novel-commercial-writing | 00-书核/, 05-市场/, 20-大纲/, 30-正文/ |
| novel-deslop | 30-正文/, 40-修订/ |
| novel-ideation | 00-书核/ |
| novel-worldbuilding | 10-设定/, 90-运行/决策记录.md |
| novel-outlining | 20-大纲/ |
| novel-checkup | 20-大纲/, 30-正文/, 40-修订/体检报告/, 90-运行/ |
| novel-drafting | 20-大纲/, 30-正文/, 90-运行/ |
| novel-revision | 30-正文/, 40-修订/, 90-运行/决策记录.md |

## 迭代建议

下一步最值得继续补强的部分：

1. 为 novel-bootstrap 增加导入旧稿到自动映射模板的半自动脚本。
2. 为 novel-market-scan 增加半自动榜单采样模板。
3. 为 novel-drafting 增加根据 chapter beat 自动组装上下文包的辅助脚本。
4. 为 novel-checkup 增加更细的 forward-test，验证卷体检、漏线扫描和追读排查的稳定性。
5. 增加真实 forward-test 样例，验证 skill 在扫榜、拆文、开书、续写、体检、改稿几种场景下的表现。

## 参考来源

这个仓库吸收了以下项目的优点，并在结构化、可维护性和项目模板层面继续前推：

- [modoojunko/awesome-novel-skill](https://github.com/modoojunko/awesome-novel-skill)
- [leenbj/novel-creator-skill](https://github.com/leenbj/novel-creator-skill)
- [PenglongHuang/chinese-novelist-skill](https://github.com/PenglongHuang/chinese-novelist-skill)
- [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)
