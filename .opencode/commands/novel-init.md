---
description: 用 novel-bootstrap 初始化一个中文小说项目
allowed-tools: Write, Bash
---

# 开书建档

为用户初始化一个中文小说项目工作区。

## 工作流程

1. 询问用户：
   - 项目目录路径
   - 书名
   - 题材
   - 一句话故事前提
   - 作者名（可选）
2. 运行初始化脚本：

```bash
python3 skills/novel-bootstrap/scripts/init_novel_project.py \
  --output <target-dir> \
  --title "<书名>" \
  --genre "<题材>" \
  --premise "<一句话前提>" \
  --author "<作者>"
```

3. 初始化后提示用户优先补的文件：
   - `00-书核/立项单.md`
   - `20-大纲/分卷/volume-01.md`
   - `20-大纲/节拍卡/chapter-001.md` 等前三章
   - `90-运行/连载驾驶舱.md`

## 注意事项

- 如果项目目录已存在且非空，询问用户是否覆盖
- 如果用户已有旧稿，建议先放到 `30-正文/导入/` 再整理
- 中文书名不要包含 `/` `\` `:` `*` `?` `"` `<` `>` `|` 等特殊字符
