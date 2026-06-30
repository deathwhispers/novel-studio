---
name: novel-revision
description: "中文小说修订 skill。用于对已有正文做结构修复、场景重写、文风校准、连续性修补、节奏调整和去 AI 味处理，适用于“这章太平”“帮我重写这一段”“检查设定冲突”“把文字修得更像成书”“降低 AI 痕迹”等场景。"
---

# 重修统稿

## 功能定位

先判断需要哪一层修订，再动笔。这个 skill 优先修问题，不优先扩篇幅；如果问题主要是 AI 质感，则应优先转交 `novel-deslop`。如果问题还没诊断清楚，先让 `novel-checkup` 做体检，再决定怎么修。

## 先选主问题模板

修订前先选一个主问题模板，不要什么都一起改：

- 因果断裂、动机悬浮、转折像作者硬推 -> `references/logic-repair-template.md`
- 细节稀薄、情绪不落地、正文大量停在总结层 -> `references/detail-repair-template.md`
- 伏笔散、回收硬、章节尾没有追读推动力 -> `references/payoff-repair-template.md`

如果三类问题同时存在，默认顺序是：逻辑 -> 回收 -> 细节 -> 句子去味。

## 三层修订梯子

1. 结构层
   - beat 是否成立
   - 章节目标是否清晰
   - 转折是否发生
   - 结尾钩子是否有效
2. 场景层
   - 对抗是否足够
   - 行动与因果是否顺
   - 信息是否在正确时机揭示
   - 对话是否有角色区分度
3. 句子层
   - 是否过度总结
   - 是否讲解味太重
   - 是否对称、平铺、泛化
   - 是否存在明显 AI 套话和安全表达

## 产物

修订时尽量同时输出：

- 修订后的正文
- `40-revision/chapter-reports/` 下对应的修订报告
- 如涉及 canon 改动，在 `90-ops/decisions.md` 记录
- 如涉及跨章因果或伏笔联动，同步更新 `20-outline/因果/scene-causality-map.md` 或 `20-outline/payoff-tracking/payoff-ledger.md`

## 去 AI 味规则

- 优先删掉解释句和概括句
- 优先把抽象判断改成动作、反应、视角内感知
- 避免所有角色共享同一套修辞和语气
- 避免段落节奏过于匀称和保险

## 边界

- 如果问题根源在大纲而非文本，转回 `novel-outlining`
- 如果问题根源在设定冲突，联动 `novel-worldbuilding`
- 如果只是继续写下一段，不转入修订循环
- 如果核心诉求是“像平台文一点”“更有人味”，可联动 `novel-commercial-writing` 或 `novel-deslop`
- 如果核心诉求是“先查有没有前后打架、有没有漏线”，先转 `novel-checkup`

需要更细的检查顺序时，读取 `references/revision-ladder.md`；需要具体修订模板时，按问题类型读取对应的 `logic-repair-template.md`、`detail-repair-template.md` 或 `payoff-repair-template.md`。

## 完本流程

当一卷结束或全书准备收尾时，按以下顺序操作：

### 第一步：线头收束

1. 逐条拉出 `20-outline/payoff-tracking/payoff-ledger.md` 检查每条埋线的回收状态
2. 检查 `20-outline/relationship-arc-tracker.md` 中每段关系的最终状态
3. 对照 `references/completion-checklist.md` 逐项完成检查

### 第二步：硬伤排查

1. 对照 `10-bible/canon.md` 检查全书的设定一致性
2. 检查 `20-outline/因果/scene-causality-map.md` 的因果链是否闭合
3. 检查角色名称、地名、能力名、时间线在全书中是否统一

### 第三步：终校

1. 全本通读，修正错别字和语病
2. 补全正文中留空的标记，删掉不再需要的 TODO
3. 将完成分卷正文移入 `50-archive/`
4. 更新 `00-story-core/project-meta.md` 状态为「已完本」

### 第四步：续集规划（可选）

- 留下的续集钩子是否足够
- 续集需要的设定变化是否已记录

## 资源
- 完本检查清单：`references/completion-checklist.md`
