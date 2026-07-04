# novel-skills

面向中文小说创作的 **写作 skill 套件**。专注于提升写作质量，覆盖扫榜、拆书、立项、设定、铺线、写章、体检、重修、商业化改稿和去 AI 味。

## 核心价值

- **质量优先**：每章 2000-2500 字，确保戏成立、逻辑闭合、细节落地
- **结构清晰**：14 个专项 skill，各司其职，协同工作
- **中文适配**：按中文写作习惯组织，适合长篇连载

## 支持的技能

| 技能 | 职责 |
|------|------|
| novel-studio | 工作台路由，根据意图分流到具体技能 |
| novel-market-scan | 扫榜、看平台差异、判断题材机会 |
| novel-deconstruction | 拆解爆款、样章，提炼可迁移技法 |
| novel-bootstrap | 初始化小说项目、导入旧稿 |
| novel-ideation | 从模糊点子收敛为创作简报 |
| novel-worldbuilding | 构建人物、世界规则、设定圣经 |
| novel-outlining | 生成主线、分卷、章节节拍卡 |
| novel-drafting | 按最小上下文包写场景或章节 |
| novel-checkup | 检查单章质量、前后照应、伏笔回收 |
| novel-revision | 结构修复、场景重写、文风校准 |
| novel-volumning | 分卷卷纲逐卷建设和迭代 |
| novel-deslop | 专做去 AI 味，修正模板感 |
| novel-commercial-writing | 书名、简介、钩子、留存优化 |
| novel-ai-writing | AI 协作写作 prompt 模板库 |

## 快速开始

### 1. 安装

```bash
# 复制 skills 目录到你的项目
python3 scripts/install.py --target-dir /path/to/your/project
```

### 2. 初始化项目

```bash
python3 skills/novel-bootstrap/scripts/init_novel_project.py \
  --output /path/to/my-novel \
  --title "书名" \
  --genre "题材" \
  --premise "一句话故事前提"
```

### 3. 开始写作

按以下顺序使用技能：

1. `novel-bootstrap` - 初始化项目
2. `novel-ideation` - 立项定核
3. `novel-worldbuilding` - 设定总表
4. `novel-outlining` - 铺线列纲
5. `novel-drafting` - 写章起稿
6. `novel-checkup` - 体检
7. `novel-revision` - 重修统稿
8. `novel-deslop` - 去 AI 味
9. `novel-commercial-writing` - 商业化改稿

## 项目结构

初始化后的项目遵循以下目录分层：

```
my-novel/
├── 00-书核/          # 核心目标与承诺
├── 05-市场/          # 市场与对标研究
├── 10-设定/          # 世界观、角色、规则
├── 20-大纲/          # 故事结构与推进
├── 30-正文/          # 正文资产
├── 40-修订/          # 体检和修稿报告
├── 50-归档/          # 已完成的内容
└── 90-运行/          # 当前进度、决策记录
```

## 章节写作标准

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

## 迭代建议

1. 为 novel-bootstrap 增加导入旧稿的半自动脚本
2. 为 novel-market-scan 增加半自动榜单采样模板
3. 为 novel-drafting 增加根据节拍卡自动组装上下文包的辅助脚本
4. 为 novel-checkup 增加更细的 forward-test

## 参考来源

这个仓库吸收了以下项目的优点：

- [modoojunko/awesome-novel-skill](https://github.com/modoojunko/awesome-novel-skill)
- [leenbj/novel-creator-skill](https://github.com/leenbj/novel-creator-skill)
- [PenglongHuang/chinese-novelist-skill](https://github.com/PenglongHuang/chinese-novelist-skill)
- [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)

## 许可证

Apache-2.0