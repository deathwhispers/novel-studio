# 快速开始

## 1. 安装

```bash
# 复制 skills 目录到你的项目
python3 scripts/install.py --target-dir /path/to/your/project
```

## 2. 初始化项目

```bash
python3 skills/novel-bootstrap/scripts/init_novel_project.py \
  --output /path/to/my-novel \
  --title "书名" \
  --genre "题材" \
  --premise "一句话故事前提"
```

## 3. 开始写作

按以下顺序使用技能：

1. `novel-bootstrap` - 初始化项目
2. `novel-ideation` - 立项定核
3. `novel-worldbuilding` - 设定总表
4. `novel-outlining` - 铺线列纲
5. `novel-chapter-workflow` - 章节质量门禁（强制执行完整流程）
6. `novel-commercial-writing` - 商业化改稿

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
