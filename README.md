# novel-skills

面向中文小说创作的 **写作 skill 套件**。专注于提升写作质量，覆盖扫榜、拆书、立项、设定、铺线、写章、体检、重修、商业化改稿和去 AI 味。

## 核心价值

- **质量优先**：每章 2000-2500 字，确保戏成立、逻辑闭合、细节落地
- **结构清晰**：8 个专项 skill，各司其职，协同工作
- **中文适配**：按中文写作习惯组织，适合长篇连载
- **互动规划**：与用户互动确认小说篇幅、分卷数量、更新频率等关键信息

## 快速开始

👉 [查看快速开始指南](QUICKSTART.md)

## 支持的技能

| 技能 | 职责 |
|------|------|
| novel-studio | 工作台路由，根据意图分流到具体技能 |
| novel-market | 市场研究、拆解爆款、商业化包装 |
| novel-project | 项目初始化、立项定核、篇幅规划 |
| novel-worldbuilding | 构建人物、世界规则、设定圣经 |
| novel-outline | 大纲规划、卷纲建设、章节节拍卡 |
| novel-writing | 写作流程、质量门禁、状态回写 |
| novel-quality | 体检、修订、去AI味 |
| novel-ai-writing | AI 协作写作 prompt 模板库 |

## 技能合并说明

为了简化使用流程，我们将原有的 15 个技能合并为 8 个：

| 原技能 | 合并后 | 职责 |
|--------|--------|------|
| novel-market-scan + novel-deconstruction + novel-commercial-writing | **novel-market** | 市场研究、拆解爆款、商业化包装 |
| novel-bootstrap + novel-ideation | **novel-project** | 项目初始化、立项定核、篇幅规划 |
| novel-worldbuilding | **novel-worldbuilding** | 设定构建（保持独立） |
| novel-outlining + novel-volumning | **novel-outline** | 大纲规划、卷纲建设 |
| novel-drafting + novel-chapter-workflow | **novel-writing** | 写作流程、质量门禁 |
| novel-checkup + novel-revision + novel-deslop | **novel-quality** | 体检、修订、去AI味 |
| novel-ai-writing | **novel-ai-writing** | AI协作prompt（保持独立） |
| novel-studio | **novel-studio** | 工作台路由（保持独立） |

## 项目结构

初始化后的项目遵循以下目录分层：

```
my-novel/
├── 00-书核/          # 核心目标与承诺
├── 05-市场/          # 市场与对标研究
├── 10-设定/          # 世界观、角色、规则
├── 20-大纲/          # 故事结构与推进
├── 30-正文/          # 正文资产
│   ├── 第一卷-卷名/   # 每卷一个目录
│   │   ├── 第001章.md
│   │   ├── 第002章.md
│   │   └── ...
│   ├── 第二卷-卷名/
│   │   ├── 第010章.md
│   │   └── ...
│   └── ...
├── 40-修订/          # 体检和修稿报告
├── 50-归档/          # 已完成的内容
└── 90-运行/          # 当前进度、决策记录
```

## 章节写作标准

### 长篇章节数量要求

**百万字长篇必须满足**：
- 总章节数 ≥ 400章
- 分卷数 ≥ 10卷
- 每卷章节数 ≥ 30章
- 每卷字数 ≥ 6万字

**章节规划验证清单**：
- [ ] 全书总章节数 ≥ 400章
- [ ] 分卷数 ≥ 10卷
- [ ] 每卷章节数 ≥ 30章
- [ ] 每卷字数 ≥ 6万字
- [ ] 每卷都有明确的功能定位
- [ ] 冲突升级路径清晰
- [ ] 角色成长弧线完整

### 字数设定

- 默认每章 **2000-2500 字**
- 确保戏成立、逻辑闭合、细节落地
- 章尾必须有推进力

### 质量底线

1. 不用整段总结代替戏
2. 不用作者解释代替人物行动
3. 不用抽象情绪词代替身体反应
4. 不让角色在没有代价的情况下突然改变
5. 章尾必须留下问题、压力、决定或余震

### 写作流程

1. **写前锁定**：明确本章任务、冲突、前后照应
2. **起稿执行**：先锁核心戏，再补细节
3. **写后自检**：检查质量标准，决定下一步
4. **状态回写**：更新进度、伏笔、因果关系

**注意**：现在推荐使用 `novel-writing` 来强制执行完整的章节写作流程，它会自动管理草稿、检查、修正、去AI味等步骤，确保每个章节都达到高质量标准。

## 体检机制

写完章节后，先体检再修订：

### 单章体检

- 检查前后照应、人物状态、伏笔回收
- 检查章尾推动力
- 输出问题清单

### 卷体检

- 检查卷级节奏、长线推进
- 检查追读压力
- 输出修订建议

## 参考来源

- [modoojunko/awesome-novel-skill](https://github.com/modoojunko/awesome-novel-skill)
- [leenbj/novel-creator-skill](https://github.com/leenbj/novel-creator-skill)
- [PenglongHuang/chinese-novelist-skill](https://github.com/PenglongHuang/chinese-novelist-skill)
- [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)

## 许可证

Apache-2.0
