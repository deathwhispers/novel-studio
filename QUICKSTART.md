# 快速开始

## 1. 安装

```bash
# 复制 skills 目录到你的项目
python3 scripts/install.py --target-dir /path/to/your/project
```

更新已安装的副本时显式使用 `--force`：

```bash
python3 scripts/install.py --target-dir /path/to/your/project --force
```

卸载时使用同一个目标目录：

```bash
python3 scripts/uninstall.py --target-dir /path/to/your/project
```

## 2. 初始化项目

```bash
python3 skills/novel-project/scripts/init_novel_project.py \
  --output /path/to/my-novel \
  --title "书名" \
  --genre "题材" \
  --premise "一句话故事前提" \
  --profile minimal \
  --mode 探索起草
```

模板档位：`minimal` 适合短篇或试写，`serial` 适合常规连载（默认），`longform` 适合多线、多人和超长篇。

## 3. 开始写作

按当前意图选择最短链路；下面是需要完整项目时的常见顺序：

1. `novel-project` - 初始化项目、立项定核、篇幅规划
2. `novel-worldbuilding` - 设定总表
3. `novel-outline` - 铺线列纲
4. `novel-writing` - 按模式优先完成正文，再做轻量硬伤检查
5. `novel-quality` - 证据型体检、最小修订、语言与形式校准
6. `novel-feedback` - 发布后追踪读者反馈并调整后续写作

短篇、文学叙事或人物试写可直接从 `novel-writing` 开始；未知但可逆的信息不阻止起草。

续写前可生成最小上下文包：

```bash
python3 scripts/build_context_pack.py /path/to/my-novel \
  --chapter 12 \
  --task "当前要写的人物、场景与意图" \
  --output /path/to/my-novel/90-运行/上下文包-chapter-012.md
```

正文完成后可扫描表层风险。该工具不输出文学质量综合分：

```bash
python3 scripts/evaluate_chapter.py /path/to/my-novel \
  --chapter 第012章 \
  --profile web-serial \
  --verbose
```

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
| novel-outline | 按模式规划作品、阶段、场景与线索结构 |
| novel-writing | 正文优先起稿、轻量硬伤检查、状态增量 |
| novel-quality | 证据型体检、最小修订、语言与形式校准 |
| novel-feedback | 读者反馈追踪、趋势分析、驱动后续优化 |
