# 快速开始

## 1. 安装

```bash
# 复制 skills 目录到你的项目
python3 scripts/install.py --target-dir /path/to/your/project
```

## 2. 初始化项目

```bash
python3 skills/novel-project/scripts/init_novel_project.py \
  --output /path/to/my-novel \
  --title "书名" \
  --genre "题材" \
  --premise "一句话故事前提"
```

## 3. 开始写作

按以下顺序使用技能：

1. `novel-project` - 初始化项目、立项定核、篇幅规划
2. `novel-worldbuilding` - 设定总表
3. `novel-outline` - 铺线列纲
4. `novel-writing` - 写章起稿（强制执行完整流程）
5. `novel-quality` - 体检、修订、去AI味

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
│   │   ├── 第001章-章节名.md
│   │   ├── 第002章-章节名.md
│   │   └── ...
│   ├── 第二卷-卷名/
│   │   ├── 第010章.md
│   │   └── ...
│   └── ...
├── 40-修订/          # 体检和修稿报告
├── 50-归档/          # 已完成的内容
└── 90-运行/          # 当前进度、决策记录
```

## 技能体系

本项目包含 8 个核心技能：

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
