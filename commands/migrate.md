---
type: command
name: migrate
description: "存量项目迁移。将已有章节逆向提取为结构化状态文件和工作区骨架。"
workflow: migrate-project
---

# /novel-studio:migrate

将已有章节的小说项目导入 novel-studio 工作区。自动识别章节文件、分批提取角色/规则/伏笔、多轮作者确认、生成完整状态文件。

## 用法

```
/novel-studio:migrate <现有目录路径>
/novel-studio:migrate .                  # 当前目录
/novel-studio:migrate ~/my-novel         # 指定目录
```

## 执行流程

1. **扫描 + 重组**：识别章节文件（按"第X章"/"Chapter X"/文件名数字前缀），创建工作区目录结构，移动章节到 `chapters/`
2. **分批正文分析**：Archivist 每批 5 章逆向提取角色、硬设定、关键事件、伏笔候选、开放问题
3. **合成归档**：Architect 合并去重 N 批提取结果，生成 `migration-extraction.yaml`
4. **多轮作者确认**：角色确认/补充 → 伏笔确认 → 秘密收集 → 大纲导入
5. **文件生成**：Architect 写入 `setting/`，StateManager 写入 `state/`

## 示例

```
/novel-studio:migrate ~/my-old-novel

📊 扫描完成：50章 / 125,000字
   识别章节：第1章 ~ 第50章

📁 工作区重组中…
✅ 目录结构已创建，章节文件已移动到 chapters/

📖 正在分批分析正文…
   批次 1/10 (第1-5章) ✅
   批次 2/10 (第6-10章) ✅
   …

🧩 正在合成归档…
✅ 识别角色 12 个 / 伏笔候选 8 条 / 硬设定 6 条

💬 请确认提取结果：
   角色是否正确？→ 修改/补充
   伏笔是否准确？→ 确认/删除/新增
   …

✅ 迁移完成！下一步：/novel-studio:write 51
```

## 注意事项

- 迁移是一次性操作，完成后工作区正常使用 `/novel-studio:write` 继续写作
- 确认环节可随时中断，下次执行 `/novel-studio:migrate` 会从断点继续
- 正文文件不会被修改，只会移动/复制到 `chapters/` 下统一命名
