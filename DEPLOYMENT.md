# 使用指南

novel-skills 是一套中文小说写作 skill 套件，专注于提升写作质量。

## 安装

### 自动安装

```bash
python3 scripts/install.py --target-dir /path/to/your/project
```

目标中已有 `novel-skills/` 时，安装器会拒绝覆盖。确认更新时使用：

```bash
python3 scripts/install.py --target-dir /path/to/your/project --force
```

卸载：

```bash
python3 scripts/uninstall.py --target-dir /path/to/your/project
```

### 手动安装

将 `skills/` 目录复制到你的项目：

```bash
cp -R skills/ /path/to/your/project/skills/
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
| novel-feedback | 读者反馈追踪、趋势分析、驱动后续优化 |

## 推荐工作流程

1. **启动工作台**：`novel-studio` 判断当前该做什么
2. **研究市场**（可选）：`novel-market` 扫榜、拆书、商业化包装
3. **初始化项目**：`novel-project` 开书、定核、篇幅规划
4. **建设设定**：`novel-worldbuilding` 角色、世界、规则
5. **铺设大纲**：`novel-outline` 全书总纲、分卷卷纲、节拍卡
6. **写作执行**：`novel-writing` 写章起稿（强制质量门禁）
7. **质量检查**：`novel-quality` 体检、修订、去AI味
8. **读者反馈**（发布后）：`novel-feedback` 收集评论和追读数据，验证调整效果

## 章节字数设定

默认每章 2000-2500 字，适用于大多数网文章节。

## 项目结构

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
│   │   ├── 第010章-章节名.md
│   │   └── ...
│   └── ...
├── 40-修订/          # 体检和修稿报告
├── 50-归档/          # 已完成的内容
└── 90-运行/          # 当前进度、决策记录
```

## 常见问题

### Q: 如何更新版本？

重新复制 `skills/` 目录即可。

### Q: 可以同时用于多个项目吗？

可以。将 `skills/` 目录复制到每个项目中即可。

### Q: 旧版本（15 skill）如何迁移？

请参考 `skills/novel-project/references/迁移旧稿指南.md`。
