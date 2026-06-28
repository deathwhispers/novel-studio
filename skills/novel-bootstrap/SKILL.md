---
name: novel-bootstrap
description: "中文小说项目初始化与导入 skill。用于从零创建小说工作区、把旧小说资料迁移到统一模板、导入散落的大纲/设定/正文文件，或检查当前目录是否已经是规范小说工程时。适用于用户说“开一本书”“初始化小说目录”“导入我现有的稿子”“把旧项目整理成长期可维护结构”等场景。"
---

# Novel Bootstrap

## Overview

先把小说工程落地，再进入创作。这个 skill 负责统一目录、模板和导入策略，不负责代替后续 skill 完成全部内容。

## 初始化流程

1. 检查当前目录是否已存在 `00-story-core/project-meta.md`
2. 如果不存在，优先初始化模板工作区
3. 如果存在，但结构不完整，先补目录，再整理已有资料
4. 如果用户带来了旧稿、角色卡、世界观文档或零散正文，先按导入清单映射，再进入后续创作阶段

## 新建项目

使用本 skill 目录里的初始化脚本：

```bash
python3 scripts/init_novel_project.py \
  --output <target-dir> \
  --title "<novel-title>" \
  --genre "<genre>" \
  --premise "<one-line-premise>"
```

如果标题、题材或一句话前提不完整，先收集到足以初始化为止，不要提前跳到写正文。

## 导入旧项目

导入时遵守以下顺序：

1. 不重写原始资料，先分类
2. 设定资料 -> `10-bible/`
3. 大纲资料 -> `20-outline/`
4. 正文资料 -> `30-draft/imported/` 或 `30-draft/chapters/`
5. 关键导入决策写进 `90-ops/decisions.md`
6. 导入后更新 `90-ops/current-state.md`

不要在导入阶段顺手大改文稿内容。先让项目可读、可找、可继续，再进入 `novel-ideation`、`novel-worldbuilding` 或 `novel-outlining`。

## 工作区完成标准

- `00-story-core/project-meta.md` 存在
- `00-story-core/creative-brief.md` 至少有初稿
- `10-bible/`、`20-outline/`、`30-draft/`、`90-ops/` 目录已就位
- `90-ops/current-state.md` 记录当前阶段和下一步
- 若是导入项目，`30-draft/imported/source-index.md` 已记录来源

## 资源

- 工作区结构说明：`references/workspace-spec.md`
- 导入映射清单：`references/import-checklist.md`
- 初始化模板：`assets/novel-project-template/`
- 初始化脚本：`scripts/init_novel_project.py`

先初始化，再创作。
