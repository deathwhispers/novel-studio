# 失败模式 ↔ 检测 Skill 对照表

> **O5 修复（2026-09）**：把 `references/failure-cases.md` 的 55 个失败模式映射到 `skills/` 下的 17 个检测 Skill，消除 Writer 自检与 Critic 检测的覆盖盲区。
>
> **目的**：
> 1. 让 Writer 写 beat 阶段自检时知道每条失败模式由谁检测
> 2. 让 Critic Lite 在写章节收尾时知道重点检查哪几项
> 3. 让用户在 `/novel-studio:check` 时能看到检测覆盖地图

---

## 一、人物类失败（#1-#7）

| # | 失败模式 | 主检测 Skill | 辅助 Skill | 检测时机 | 备注 |
|---|---------|------------|-----------|---------|------|
| 1 | 工具人配角 | `character-check` | — | Writer 写前自检 + Critic Lite | 配角独立动机缺失 |
| 2 | 扁平反派 | `character-check` | — | Writer 写前自检 + Critic Lite | 反派内在逻辑缺失 |
| 3 | 突然变蠢的主角 | `character-check` | — | Critic Lite（前后章对比） | 行为与既有设定不符 |
| 4 | 突然圣父的主角 | `character-check` | — | Critic Lite（前后章对比） | 心理变化缺失铺垫 |
| 5 | 突然黑化的角色 | `character-check` | — | Critic Lite（前后章对比） | 渐变过程缺失 |
| 6 | 花瓶女主 | `character-check` | — | Writer 写前自检 | 独立弧线缺失 |
| 7 | 同质化配角 | `voice-check` | `character-check` | Writer 写前自检 | 独特语言特征缺失 |

## 二、剧情类失败（#8-#15）

| # | 失败模式 | 主检测 Skill | 辅助 Skill | 检测时机 | 备注 |
|---|---------|------------|-----------|---------|------|
| 8 | 硬开金手指 | `causality-check` | — | Critic Lite | 获得过程与代价缺失 |
| 9 | 突然变强 | `causality-check` | — | Critic Lite | 升级门槛与过程缺失 |
| 10 | 反派突然变弱 | `causality-check` | — | Critic Lite | 失败代价/铺垫缺失 |
| 11 | 剧情无后果 | `causality-check` | — | Writer 写前自检 | 场面未改变局面 |
| 12 | 主角无代价 | `causality-check` | — | Writer 写前自检 | 胜利无代价 |
| 13 | 剧情强行推进 | `causality-check` | `character-check` | Writer 写前自检 | 角色动机缺失 |
| 14 | 中段空转 | `pacing-check` | — | Critic Lite（按章功能） | 5+ 章未推进 |
| 15 | 剧情过密 | `pacing-check` | — | Writer 写前自检 | 一章 3+ 个新事件 |

## 三、伏笔类失败（#16-#20）

| # | 失败模式 | 主检测 Skill | 辅助 Skill | 检测时机 | 备注 |
|---|---------|------------|-----------|---------|------|
| 16 | 埋了但忘了 | `foreshadow-check` | — | Critic Lite（跨章扫描）+ `/check` | 跨章伏笔追踪 |
| 17 | 硬回收 | `foreshadow-check` | — | Critic Lite（本章扫描） | 回收前暗示缺失 |
| 18 | 假答案写太死 | ⚠️ **无对应 skill** | Writer 自检 | Writer 写前自检 | **覆盖盲区**——建议在 `foreshadow-check` 加"假答案翻案空间"检测项 |
| 19 | 伏笔太多 | ⚠️ **无对应 skill** | Writer 自检 | Writer 写前自检 | **覆盖盲区**——建议在 `foreshadow-check` 加"密度"阈值 |
| 20 | 伏笔太隐晦 | `foreshadow-check` | — | Writer 写前自检 | 显隐两层缺失 |

## 四、感情类失败（#21-#26）

| # | 失败模式 | 主检测 Skill | 辅助 Skill | 检测时机 | 备注 |
|---|---------|------------|-----------|---------|------|
| 21 | 突然恋爱 | `emotion-payoff` | `causality-check` | Critic Lite | 暧昧期缺失 |
| 22 | 一见钟情 | `emotion-payoff` | — | Critic Lite | 感情渐变缺失 |
| 23 | 三角恋混乱 | ⚠️ **无对应 skill** | Writer 自检 | Writer 写前自检 | **覆盖盲区**——建议在 `character-check` 加"关系网复杂度"检查 |
| 24 | 感情线停滞 | `emotion-payoff` | — | `/check` | 10+ 章未推进 |
| 25 | 强行 BE | `emotion-payoff` | `causality-check` | Critic Lite | BE 前因缺失 |
| 26 | 感情线无逻辑 | ⚠️ **无对应 skill** | Writer 自检 | Writer 写前自检 | **覆盖盲区**——建议在 `emotion-payoff` 加"事件触发检查" |

## 五、技法类失败（#27-#36）

| # | 失败模式 | 主检测 Skill | 辅助 Skill | 检测时机 | 备注 |
|---|---------|------------|-----------|---------|------|
| 27 | 抽象情绪 | `description` | `scene-render` | Writer 写前自检 + ai-flavor-detect | 具体感官缺失 |
| 28 | 作者附身 | `pov-control` | — | Critic Lite | 旁白入侵 |
| 29 | 套路化 | `stylist` | Writer 自检 | Writer 写前自检 | **覆盖盲区**——`stylist` 只覆盖润色，无"套路识别"检测；建议新增 |
| 30 | 多线齐开 | `pacing-check` | — | Writer 写前自检 | 第 1 章主线过多 |
| 31 | 作者说教 | `pov-control` | `dialogue` | Critic Lite | 角色代言作者意图 |
| 32 | 模板化语言 | `ai-flavor-detect` | `stylist` | Critic Lite | 与 `ai-flavor-checklist.md` 24 项关键词检测粒度不同——本项更广义（"段落可移植到任何作品"），需 `stylist` 人工判别 |
| 33 | 对话过密 | `dialogue` | — | Writer 写前自检 | 对话未承担关系/信息变化 |
| 34 | 对话过疏 | `dialogue` | — | Writer 写前自检 | 章节功能需要对话时缺失 |
| 35 | 动作戏过水 | `action-scene` | — | Writer 写前自检 | 战斗过程/代价缺失 |
| 36 | 动作戏过密 | `action-scene` | `pacing-check` | Writer 写前自检 | 招式细节超载 |

## 六、结构类失败（#37-#40）

| # | 失败模式 | 主检测 Skill | 辅助 Skill | 检测时机 | 备注 |
|---|---------|------------|-----------|---------|------|
| 37 | 烂尾 | `pacing-check` | `hook-design` | `/check` | 结局铺垫缺失 |
| 38 | 强行反转 | `causality-check` | `foreshadow-check` | Critic Lite | 反转前暗示缺失；**覆盖盲区**——`causality-check` 关注因果连续，反转合理性需 Writer 自检补 |
| 39 | 草草收束 | `character-check` | `pacing-check` | `/check` | 主要角色归宿缺失 |
| 40 | 续集留白太多 | ⚠️ **无对应 skill** | Writer 自检 | Writer 写前自检 | **覆盖盲区**——续集钩子数量无对应检测项；建议在 `pacing-check` 加"续集钩子密度" |

## 七、风格类失败（#41-#45）

| # | 失败模式 | 主检测 Skill | 辅助 Skill | 检测时机 | 备注 |
|---|---------|------------|-----------|---------|------|
| 41 | 风格漂移 | `style-calibrate` | `voice-check` | Critic Lite | 文风前后不一致 |
| 42 | 节奏不稳 | `pacing-check` | — | Writer 写前自检 | 篇幅基线缺失 |
| 43 | 人物前后矛盾 | `character-check` | — | Critic Lite（前后章对比） | 行动逻辑违反角色卡 |
| 44 | 信息矛盾 | `info-leak-check` | `panel-consistency` | Critic Lite | 与硬规则/面板冲突 |
| 45 | 地理矛盾 | ⚠️ **无对应 skill** | Writer 自检 + setting | Writer 写前自检 | **覆盖盲区**——`setting/地点距离表.md` 是约束源，但无对应检测 skill；建议新增 `geo-consistency` skill 或在 `info-leak-check` 加"地理一致性"子项 |

## 八、对话类失败（#46-#51）

| # | 失败模式 | 主检测 Skill | 辅助 Skill | 检测时机 | 备注 |
|---|---------|------------|-----------|---------|------|
| 46 | 直说情绪 | `dialogue` | `description` | Critic Lite | 对话承载情绪而非行为 |
| 47 | 作者腔 | `voice-check` | `dialogue` | Critic Lite | 语言不符合角色处境 |
| 48 | 同质化 | `voice-check` | — | Writer 写前自检 | 角色无独特语言特征 |
| 49 | 信息大爆炸 | `dialogue` | `info-leak-check` | Writer 写前自检 | 单段对话塞过多背景 |
| 50 | 嘴炮对话 | `causality-check` | — | Writer 写前自检 | 承诺无行动支撑 |
| 51 | 故作留白 | `dialogue` | `voice-check` | Critic Lite | 省略号/单字回应无实质回避内容 |

## 九、腔调类失败（#52-#55）

| # | 失败模式 | 主检测 Skill | 辅助 Skill | 检测时机 | 备注 |
|---|---------|------------|-----------|---------|------|
| 52 | 假装洞察 | `voice-check` | `stylist` | Critic Lite | "不是A。是B。"句式无内容 |
| 53 | 假装极简 | `stylist` | `scene-render` | Critic Lite | 极短独立句无重量 |
| 54 | 空转对话 | `dialogue` | — | Critic Lite | 对话无信息/关系推进 |
| 55 | 替读者判断 | `description` | `stylist` | Critic Lite | 动作+解释组合，删解释 |

---

## 覆盖盲区汇总（10 项需新增/扩展）

> 这 10 项失败模式当前**无自动检测 skill 覆盖**，只能依赖 Writer 写前自检。建议在未来迭代中：

| # | 失败模式 | 建议改动 |
|---|---------|---------|
| 18 | 假答案写太死 | `foreshadow-check` 加"假答案翻案空间"检测项 |
| 19 | 伏笔太多 | `foreshadow-check` 加"密度"阈值（每章 ≤2 新伏笔） |
| 23 | 三角恋混乱 | `character-check` 加"关系网复杂度"检查 |
| 26 | 感情线无逻辑 | `emotion-payoff` 加"事件触发检查" |
| 29 | 套路化 | 新增 `tropes-detect` skill 或扩 `stylist` |
| 38 | 强行反转 | `causality-check` 加"反转合理性"子项 |
| 40 | 续集留白太多 | `pacing-check` 加"续集钩子密度" |
| 45 | 地理矛盾 | 新增 `geo-consistency` skill 或扩 `info-leak-check` |
| 4 | 突然圣父 | — | character-check 已覆盖 |
| 5 | 突然黑化 | — | character-check 已覆盖 |

---

## A4 修复：Critic checklist 子项整合

> **问题**：上表 10 项盲区当前只能依赖 Writer 写前自检，Critic 不检查。但部分失败模式（如"假答案写太死"、"伏笔太多"）可以在 Critic Lite 阶段做轻量检测。
>
> **A4 修复**：把 5 项可在 Critic 轻量阶段检测的失败模式整合进 Critic Lite checklist，作为各对应 Checker 的**子项**（不是新 skill，而是已有 skill 的扩展检查）。其余 5 项（需要深度语义判断）保留为 Writer 自检。

| # | 失败模式 | Critic Lite 子项归属 | 检测方式 |
|---|---------|-------------------|---------|
| 18 | 假答案写太死 | `foreshadow-check` 子项 | 扫描本章被"假回收"的伏笔，是否有翻案空间（叙述者视角未绝对定论） |
| 19 | 伏笔太多 | `foreshadow-check` 子项 | 本章 `foreshadow.yaml` 新增条目 > 2 → 硬伤，标记就地修 |
| 23 | 三角恋混乱 | `character-check` 子项 | 主角关系网超 4 个暧昧对象且无独立动机 → 软问题，标注修复建议 |
| 26 | 感情线无逻辑 | `emotion-payoff` 子项 | 感情变化必须有事件触发；本章是否有触发事件支撑？无 → 软问题 |
| 38 | 强行反转 | `causality-check` 子项 | 反转前 5 章内是否有暗示？无 → 硬伤，标记就地修 |

**剩余 5 项保留为 Writer 写前自检**：
- 29 套路化（需要语义层面识别"烂大街桥段"，LLM 难做）
- 40 续集留白太多（跨卷视角，写完数完）
- 45 地理矛盾（需对照 `setting/地点距离表.md`，距离对照）
- 1-7 人物类细节失败（写作中判断，Critic 不易量化）
- 14 中段空转（跨 5+ 章检测，Critic Lite 跨章上下文不足）

**实现**：Critic Lite 阶段，每个 Checker 必查子项清单如下（详见 `agents/critic.md` 各 Checker 段）：

| Checker | 必查子项（含盲区） |
|---------|-----------------|
| `causality-check` | 因果链 + 时间/地点 + 关键事件 + **反转合理性（38）** |
| `foreshadow-check` | 跨章追踪 + 本章回收 + **假答案翻案空间（18）** + **密度阈值（19）** |
| `character-check` | 角色一致性 + 行动逻辑 + **关系网复杂度（23）** |
| `emotion-payoff` | 情绪节奏 + 爽点兑现 + **感情线触发事件（26）** |
| `info-leak-check` | POV 信息边界 + 硬规则 + 地理一致性 + **地理矛盾（45）** |

**O5 + A4 整合后的 Critic Lite 工作流**：
1. 检测 skill 的核心检查项（每个 skill 自带）
2. + 上表 5 项盲区子项（属于对应 Checker 扩展）
3. + 仍保留为 Writer 自检的 5 项（不进入 Critic Lite）

Critic Lite 报告输出 `lite_report` 时，对应 Checker 的 `issues` 数组里会包含上述子项的检测结果。

---

## 与 `ai-flavor-checklist.md` 的关系

`ai-flavor-checklist.md` 是 AI 味检测清单（24 项关键词扫描），与本对照表互补：
- **AI 味检测**：扫描具体词汇与句式（如"眼中闪过一丝复杂"超 5 次）
- **失败模式检测**：扫描叙事逻辑（如"突然圣父"、"剧情强行推进"）

两者粒度不同：
- AI 味是**字面层**（词汇/句式）
- 失败模式是**结构层**（角色/情节/对话）

**建议**：Critic Lite 同时跑这两套检测，避免单层覆盖盲区。

---

## 使用建议

### Writer 写 beat 前自检（10 项盲区必须自检）

Writer 写 beat 前对照本表"主检测 Skill"列 + 10 项盲区清单，写完后用 `/novel-studio:check` 复核。

### Critic Lite 阶段

按本表"检测时机"列确定每条失败模式的检查权重：
- `Writer 写前自检`：Critic Lite 只做轻量复核（不重复检查）
- `Critic Lite`：必检项
- `/check`：完整质量扫描时检测

### 用户使用 `/novel-studio:check`

显示检测覆盖地图：本对照表 + 已检 skill + 盲区提示（10 项需用户自行判断）。

---

**维护说明**：本对照表由 O5 修复创建于 2026-09，未来新增 skill 或失败模式时同步更新。