<div align="center">
  <h1>Novel Studio</h1>
  <p><strong>面向中文长篇小说的 AI 写作多智能体系统</strong></p>
  <p>7 个 Agent 各司其职，7 条命令覆盖从立项到成稿的完整创作流程</p>
  <p>
    <img src="https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square" />
    <img src="https://img.shields.io/badge/version-0.0.6-green?style=flat-square" />
    <img src="https://img.shields.io/badge/platform-Claude%20Code-orange?style=flat-square" />
  </p>
</div>

---

## 为什么选择 Novel Studio

用 AI 写长篇小说最痛苦的不是文笔，是**失控**。

写到第 50 章忘了第 3 章埋的伏笔，角色性格悄然漂移，信息释放节奏混乱，上下文越写越长直到模型崩溃。更致命的是——AI 一次性写完一章，跑偏了整章都得重来。

Novel Studio 把复杂度拆成 **7 个各司其职的 Agent**，每个 Agent 只看到任务所需的最小上下文。写作不再是"一键生成然后祈祷"，而是**多轮深度对话**——你定方向，AI 写一小段，你检查纠偏，确认后再写下一段。跑偏最多偏 400 字。

> 不是自动流水线。是你和 AI 的协作工作台。

## 快速安装

```bash
# 安装
claude plugin install novel-studio@deathwhispers/novel-studio

# 更新
claude plugin update novel-studio

# 强制重装（当 update 提示已是最新版但实际需要更新时）
claude plugin uninstall novel-studio && claude plugin install novel-studio@deathwhispers/novel-studio

# 卸载
claude plugin uninstall novel-studio
```

## 三条命令走完一章

```bash
# 1. 确认本章方向（多轮对话，3-5 轮）
/novel-studio:write 10

# 2. 逐段写作（你描述 → AI 写 200-400 字 → 你检查 → 下一段）
→ 「从主角推开仓库门开始写」
✍️ 第 10 章 · 第 1 段：[正文 350 字]
→ 「这段可以，继续。接下来写他发现地上的血迹」
✍️ 第 10 章 · 第 2 段：[正文 280 字]
→ 「这段不对，血迹应该是新鲜的，不是干涸的」
✅ 已修正
→ ...循环直到你说「这章到此结束」

# 3. 查看本章统计，锁定
✅ 第 10 章完成（约 2200 字）
```

## 命令一览

| 命令 | 用途 | 对话深度 |
|:------|:------|:---------|
| `/novel-studio:init` | 初始化新项目 — 创作起点、核心体验、品类基调、主角灵魂、篇幅模式 | 5 轮 |
| `/novel-studio:world` | 世界观构建 — 角色、力量体系、世界扩展、冲突检测、综合审查 | 每设定不限轮次 |
| `/novel-studio:outline` | 多线大纲 — 全书总纲、逐卷细化、伏笔布局、角色弧光，支持创建/调整/检查 | 逐层深化 |
| `/novel-studio:write <N>` | 写章节 — 多轮对话确定方向 + 逐段写作即时纠偏 | 不限轮次 |
| `/novel-studio:check <N>` | 质量扫描 — 问清楚用户关注什么，针对性检查，只报问题 | 1-2 轮 |
| `/novel-studio:revise <N>` | 修订章节 — 理解问题 → 判断范围 → 告知影响 → 等待确认，支持范围升级 | 2-4 轮 |
| `/novel-studio:upgrade` | 旧版升级 — v2 旧结构无损升级到 v3，保留续写状态 | 2-3 轮 |

## 架构：Agent 体系

每个 Agent 只掌握职责范围内的信息，通过 Orchestrator 裁剪的**交接包**通信。

| Agent | 职责 | 所有权 | 关键约束 |
|:-------|:------|:--------|:----------|
| **Orchestrator** | 入口、意图识别、信息裁剪 | `progress.yaml`, `agent-log` | 不创作、不检查、不修改大状态 |
| **Architect** | Canon 唯一所有者 | `core/`, `setting/` | 不读正文、不写大纲 |
| **Outliner** | 多线叙事大纲 | `outline/` | 不读正文、不改 canon |
| **ScenePlanner** | 场景五拍骨架（仅修订） | 场景节拍 | 不写正文 |
| **Writer** | 正文唯一执行者（逐段/修订双模式） | `chapters/` | 不知道第 50 章的反转 |
| **Critic** | 5 Checker 质量门禁 + 写章节收尾 Lite 检查 | 验收标准 | 只标注不修改正文 |
| **StateManager** | 状态更新 + 记忆压缩 | `state/`（大状态唯一写入口） | 写章节：用户锁定确认；修订：Critic 通过 |

## 工作区结构

```
my-novel/
├── core/                    作品核心（灵魂契约：一句话概括/读者承诺/基调/主角内核/主线承诺/禁忌与红线）
├── setting/                 硬规则、角色档案、世界规则、力量体系
├── outline/                 全书总纲、分卷大纲、故事线交错、伏笔地图、角色弧光
├── chapters/                已完成章节正文
├── snippets/                灵感片段、废弃草稿
└── state/                   运行时状态（系统自动维护）
    ├── author.yaml          作者秘密、伏笔计划、备忘
    ├── reader.yaml          读者已知事实、猜测、待解答问题
    ├── character.yaml       角色位置、状态、关系、压力项
    ├── foreshadow.yaml      伏笔追踪（埋设 → 触碰 → 揭示 → 归档）
    ├── progress.yaml        写作进度（当前章、总字数、章节状态）
    ├── transaction-log.yaml 状态事务日志（事务版本号 + 变更记录）
    └── agent-log.yaml       Agent 运行日志（支持断点恢复）
```

## 关键设计

| # | 设计 | 说明 |
|:--|:-----|:-----|
| 1 | **用户主导每一步** | 命令 = 多轮深度对话，不搞一键生成。方向、设定、大纲、写作全部由用户确认推动 |
| 2 | **逐段写作，即时纠偏** | 每段 200-400 字，写完就停。跑偏最多偏一段，改完再继续 |
| 3 | **Agent 不自选后继** | 流转由命令和用户确认决定，Agent 不自行调用下一个 Agent |
| 4 | **StateManager 唯一写入口** | 大状态（author/reader/character/foreshadow）唯一写入口，其他 Agent 只标记增量；状态更新走版本化事务（state_version + transaction-log） |
| 5 | **Writer 不读大纲** | 只知道当前段的约束和禁止触碰清单，不知道全书走向 |
| 6 | **Critic 门禁（修订/检查/写章收尾）** | 修订/检查：5 Checker 全量；写章节逐段模式：整章收尾 Critic Lite 三项轻量检查 |
| 7 | **信息裁剪** | Orchestrator 从上游完整输出中裁剪下游真正需要的字段，累计上下文从 ~34K 降至 ~25K |

## 写作质量体系

### AI 味检测

三层递进：**目录**（`ai-flavor-catalog.md`，13 类模式）→ **清单**（`ai-flavor-checklist.md`，24 项关键词+9 项结构扫描）→ **修复**（`de-flavor-techniques.md`，13 章正面修复技法）。

不仅做减法（删除解释腔、模板句式、机械罗列），更做加法——**活人感注入**：感官轮换、闲笔、身体反应优先、内心声音、不完美保留。

### 网文排版规范

`web-novel-formatting.md` — Writer 硬约束，排版违规 = 硬伤退回：

- 短句式：每句 ≤30 字，2-8 字极短句 ≥20%，30+ 字禁止
- 段落节奏：每段 ≤3 句，场景切换加空行
- 系统文字统一用【】包裹
- 对话一人一句一段，标签精简
- 章节无回顾式开头、无评书式收尾

### 老司机词汇检测

`lib/double-entendre-catalog.md` — 检测成人向暗示词汇的密度和人设匹配度。不为堆梗，为角色和场景服务。

### 描写素材库

`material-index.md` — 描写素材统一检索索引。人物（美女/性格）、穿搭、资产（汽车/名表/房产/奢侈服饰/神豪消费）、环境、美食、老司机词汇十一类素材统一用 tag 检索：先读索引 → 按 `tag` 命中条目标题 → `grep -n` 拿行号只读目标段落，不整库加载。

写作时按 tag 命中、即取即用的描写素材，与去味体系配套（每个条目带 tag + 去味示范，避免模板句和陈旧意象）：

- `lib/beauty-description-library.md` — 美女描写（89 类：身份/气质/身材/局部焦点四维度，每类带 `tag` + 完整示范 + 短句速写 + 侧面反应三种写法；眼睛/五官部位专题为要点式）
- `lib/personality-description-library.md` — 性格描写（23 类人格特质：温度/心机/呈现/底色四维度，每类带 `tag` + 完整示范 + 短句速写 + 侧面反应三种写法）
- `lib/outfit-description-library.md` — 穿搭描写（30 风格 × 3 示范，按题材/风格打 `tag`）
- `lib/car-description-library.md` — 汽车描写（12 个豪华/超跑品牌：品牌定位 + 代表车型价格带 + 描写示范）
- `lib/watch-description-library.md` — 名表描写（10 个奢侈名表品牌：品牌定位 + 代表表款价格带 + 描写示范）
- `lib/property-description-library.md` — 房产描写（7 类资产档次：类型/地段/价格带 + 描写示范）
- `lib/luxury-fashion-description-library.md` — 奢侈服饰（10 个顶级/高奢品牌：Hermès/Chanel/Dior/LV/Gucci 等，服装+包+鞋+配饰）
- `lib/luxury-consumption-library.md` — 神豪消费符号（10 类：名酒/雪茄/游艇/私人飞机/会所/马术/高尔夫/高端餐厅）
- `lib/environment-description-library.md` — 环境描写（19 类都市场景/天气/时段，每类带 `tag` + 去味示范）
- `lib/food-description-library.md` — 美食描写（8 类：火锅/烧烤/夜宵/小吃/家常/地方菜/甜品）
- `wenyin-live-platform.md` — 直播平台机制设定（稳音：礼物/特效/等级/神秘商店/展馆）

## 品类配方

当前内置 **番茄系统爽文** 品类（`genres/番茄系统爽文/`）：

- `recipe.md` — 品类核心配方：爽点类型、升级节奏、打脸频率
- `tropes.md` — 系统文常见变体：签到/抽奖/任务/神豪/吞噬流
- `rhythm.md` — 节奏约束：爽点密度、章节落点规则
- `panels.md` — 系统面板模板（init 时实例化为 setting/系统面板.md）
- `examples.md` — 经典作品参考

扩展品类：复制 `genres/_template/`，按模板填写即可。

## 项目结构

```
novel-studio/
├── agents/                   7 个 Agent 定义
│   ├── orchestrator.md       入口路由 + 信息裁剪
│   ├── architect.md          Canon 唯一所有者
│   ├── outliner.md           多线大纲设计
│   ├── scene-planner.md      场景五拍骨架
│   ├── writer.md             正文执行者
│   ├── critic.md             5 Checker 质量门禁
│   └── state-manager.md      状态持久化
├── commands/                 7 个用户命令
│   ├── init.md               项目初始化
│   ├── world.md              世界观构建
│   ├── outline.md            大纲设计
│   ├── write.md              章节写作
│   ├── check.md              质量检查
│   ├── revise.md             章节修订
│   └── upgrade.md            旧版升级
├── workflows/                8 个文件（pipeline.md 总流水线 + 7 个工作流）
│   ├── pipeline.md           总流水线
│   ├── init-project.md       项目初始化
│   ├── worldbuilding.md      世界观构建
│   ├── outline.md            大纲设计
│   ├── write-chapter.md      章节写作
│   ├── check.md              质量检查
│   ├── revise-chapter.md     章节修订
│   └── upgrade-project.md    旧版升级
├── references/               参考规范（Agent 运行时加载）
│   ├── ai-flavor-catalog.md      AI 味模式目录（13 类）
│   ├── ai-flavor-checklist.md    AI 味检测清单（24+9 项）
│   ├── de-flavor-techniques.md   去味修复技法（13 章）
│   ├── web-novel-formatting.md   网文排版规范（11 章）
│   ├── material-index.md         描写素材统一检索索引（tag 检索）
│   ├── wenyin-live-platform.md   直播平台机制设定（稳音）
│   ├── failure-cases.md          失败案例库
│   └── lib/                      描写素材库（11 个，tag 检索）
│       ├── beauty-description-library.md  美女描写素材库（89 类）
│       ├── personality-description-library.md 性格描写素材库（23 类）
│       ├── outfit-description-library.md  穿搭描写素材库（30 风格）
│       ├── car-description-library.md     汽车描写素材库（12 品牌）
│       ├── watch-description-library.md   名表描写素材库（10 品牌）
│       ├── property-description-library.md 房产描写素材库（7 类）
│       ├── luxury-fashion-description-library.md 奢侈服饰品牌素材库（10 品牌）
│       ├── luxury-consumption-library.md  神豪消费符号素材库（10 类）
│       ├── environment-description-library.md 环境描写素材库（19 类）
│       ├── food-description-library.md    美食描写素材库（8 类）
│       └── double-entendre-catalog.md     老司机词汇总表
├── skills/                   15 个纯能力 Skill
│   ├── analysis/             分析类（AI味/因果/人物/伏笔/信息泄漏/节奏/声音）
│   ├── craft/                技法类（钩子/文风校准）
│   └── narrative/            叙事类（对话/情绪兑现/POV 控制/场景渲染/动作/描写）
├── runtime/                  运行时规范
│   ├── context-budget.md     上下文预算
│   ├── handoff-schema.md     交接包 Schema
│   ├── memory-compress.md    记忆压缩协议
│   └── state-schema.md       状态文件 Schema
├── genres/                   品类配方
└── .claude-plugin/           Claude Code 插件配置
```

## 更新日志

### 0.0.6

- **角色标签**：角色档案新增 `tags` 字段（阵营 / 与主角关系 / 故事功能三维固定 + 自由关键词），写作与检查时由 Orchestrator 提取进交接包 `character_tags`，快速把握角色定位，省去重读完整档案。
- **素材库检索工程化**：`material-index.md` 去行号硬绑定，改用 `grep -n` 动态定位段落行号；素材库增删条目不再导致索引错位，仅条目标题重命名/增删时才需同步索引。
- **状态对象生命周期**：`state/` 下所有状态文件统一为「活跃对象表」，对象走 `active → settled` 生命周期，判定只有一句「下一章还用得上吗」；settled 降级为 `id + 一句话 + 章节号` 指针进 `archive/`，不复制详情，归档永不膨胀。记忆压缩从四节分文件规则收敛为统一结算协议。

### 0.0.5

- **写章节收尾 Critic Lite**：逐段写作模式整章拼接后、锁章前自动执行三项轻量检查（因果与时空连续性 / 人物一致性 / 文风与排版），按「通过 / 就地修 / 用户自决」三档判决，取代原先 Writer 交稿前的单一自检。
- **状态事务版本机制**：`progress.yaml` 新增 `state_version` 事务版本号 + 新增 `transaction-log.yaml` 事务日志；StateManager 每次状态更新作为一次版本化事务（写前核对事务号、写后递增、追加变更记录），对抗过时状态残留、多文件更新不同步、无版本可回溯、旧状态覆盖新状态四类历史记忆干扰。

### 0.0.4

- 新增描写素材库（美女 / 穿搭等），`material-index.md` 统一行号检索；移除 migrate 存量导入流程。

## 许可

Apache-2.0 © 2025 deathwhispers
