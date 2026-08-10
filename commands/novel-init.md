---
type: command
name: novel-init
description: "初始化一个新的小说项目。Orchestrator 多轮确认 → Architect 创建工作区骨架。"
workflow: init-project
---

# /novel init

初始化一个新的小说项目。调用 `workflows/init-project.md`。

## 用法

```
/novel init
```

## 执行流程

1. **Orchestrator 多轮确认**：
   - 品类（番茄系统爽文/玄幻/都市/言情/悬疑/其它）
   - 主角定位（身份/初始处境/核心优势）
   - 篇幅（短/中/长/超长）
   - 模式（商业连载/类型长篇/文学叙事/短篇/探索起草）

2. **Architect 创建工作区**：
   - `00-书核/作品总表.md`
   - `10-设定/` 完整骨架
   - 如果选择了品类 → 按品类配方初始化

3. **StateManager 初始化状态**：
   - 创建全部 runtime 状态文件

## 示例

```
/novel init

[Orchestrator] 你想写什么品类？
→ 番茄系统爽文

[Orchestrator] 主角的初始定位？
→ 穿越到修真界的高中生，靠签到系统崛起

[Orchestrator] 预计篇幅？（默认：长篇200-500章）
→ 300章

[Orchestrator] 写作模式？（默认：商业连载）
→ 商业连载

✅ 项目初始化完成！下一步：/novel world 继续完善设定，或 /novel write 1 直接开始写。
```
