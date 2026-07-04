# 使用指南

novel-skills 是一套中文小说写作 skill 套件，专注于提升写作质量。

## 快速开始

### 1. 复制 skills 目录

将 `skills/` 目录复制到你的 AI 工具的 skills 目录：

```bash
# 使用安装脚本
python3 scripts/install.py --target-dir /path/to/your/project

# 或手动复制
cp -R skills/ /path/to/your/project/skills/
```

### 2. 在 AI 工具中使用

复制后，在你的 AI 工具中可以直接调用各个 skill：

- **工作台路由**：`用 novel-studio 帮我判断下一步该走哪个 skill`
- **初始化项目**：`用 novel-bootstrap 初始化一个新小说项目`
- **写章节**：`用 novel-drafting 写下一章`
- **体检**：`用 novel-checkup 检查这一章`

## 目录结构

安装后，你的项目会包含以下 skills：

```
your-project/
├── skills/
│   ├── novel-studio/           # 工作台路由
│   ├── novel-bootstrap/        # 开书建档
│   ├── novel-worldbuilding/    # 设定总表
│   ├── novel-outlining/        # 铺线列纲
│   ├── novel-drafting/         # 写章起稿
│   ├── novel-checkup/          # 体检
│   ├── novel-revision/         # 修订
│   ├── novel-ideation/         # 立项
│   ├── novel-market-scan/      # 扫榜
│   ├── novel-deconstruction/   # 拆文
│   ├── novel-commercial-writing/  # 商业化
│   ├── novel-deslop/           # 去 AI 味
│   ├── novel-volumning/        # 卷纲
│   └── novel-ai-writing/       # AI 协作
└── ...
```

## 使用流程

推荐的工作流程：

1. **初始化项目**：`novel-bootstrap`
2. **立项定核**：`novel-ideation`
3. **设定总表**：`novel-worldbuilding`
4. **铺线列纲**：`novel-outlining`
5. **写章起稿**：`novel-drafting`
6. **体检**：`novel-checkup`
7. **重修统稿**：`novel-revision`
8. **去 AI 味**：`novel-deslop`
9. **商业化改稿**：`novel-commercial-writing`

## 章节字数设定

默认每章字数设定为 **2000-2500 字**，适用于大多数网文章节。

## 常见问题

### Q: 如何更新版本？

重新复制 `skills/` 目录即可。

### Q: 可以同时用于多个项目吗？

可以。将 `skills/` 目录复制到每个项目中即可。

### Q: 遇到问题怎么办？

查看各 skill 目录下的 `SKILL.md` 文件了解详细用法。