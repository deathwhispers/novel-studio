# 安装与使用指南

## 安装

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

## 初始化小说项目

```bash
python3 skills/novel-project/scripts/init_novel_project.py \
  --output /path/to/my-novel \
  --title "书名" \
  --genre "题材" \
  --premise "故事前提" \
  --profile minimal \
  --mode 短篇
```

可选写作模式：商业连载、类型长篇、文学叙事、短篇、探索起草。

## 使用方式

根据当前任务选择最短链路：

1. 新项目需要保存最小书核：`novel-project`。
2. 人物或设定影响当前正文：`novel-worldbuilding`。
3. 需要作品、阶段、章节或场景结构：`novel-outline`。
4. 写新正文或试写人物声音：`novel-writing`。
5. 审查、润色或重写已有正文：`novel-quality`。
6. 明确需要平台、榜单或商业包装：`novel-market`。
7. 已有读者反馈或数据：`novel-feedback`。

短篇、文学叙事与探索起草不需要先完成分卷、节拍卡或更新计划。字数是媒介与生产预算，不是通用文学质量门禁。

## 更新后的验证

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
```

项目级校验：

```bash
python3 scripts/validate_novel_project.py /path/to/my-novel
```

serial 与 longform 项目会根据 `90-运行/项目配置.md` 检查连载驾驶舱；minimal 项目不会被可选连载资料阻塞。

## 常见问题

### 更新会覆盖现有项目正文吗？

安装脚本更新的是目标中的 `novel-skills/skills` 副本，不会操作独立小说项目。使用 `--force` 前仍应确认目标路径。

### 一定要使用项目目录吗？

不需要。单段试写、短篇和局部审查可以直接调用对应 skill。项目目录主要服务长篇连续性与跨会话状态。

### 默认每章多少字？

没有跨模式默认值。商业连载可在立项单中设置可持续区间；投稿或平台硬限制按实际要求记录。
