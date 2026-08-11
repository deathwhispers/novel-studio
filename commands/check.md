---
type: command
name: check
description: "对指定章节做质量检查（Critic only），不修改正文。"
workflow: revise-chapter
---

# /novel-studio:check

对已完成的章节做质量检查，只输出 Review Report，不修改正文。

## 用法

```
/novel-studio:check <章节号>
/novel-studio:check               # 检查最新完成的章节
```

## 执行流程

仅执行 Critic 的 5 个 Checker：
1. Logic Checker（因果与连续性）
2. Info Leak Checker（信息泄漏）
3. Character Checker（人物一致性）
4. Pace Checker（节奏）
5. Style Checker（文风/AI味）

## 示例

```
/novel-studio:check 10

🔍 第10章质量检查：

✅ Logic：通过（因果链完整，无硬设定冲突）
✅ Info Leak：通过（未触碰禁止清单）
⚠️  Character：软问题1处——配角XX的行为缺少动机铺垫
⚠️  Pace：场景2冲突升级偏快（计划1200字/实际800字）
⚠️  Style：AI味4处（2处解释腔 + 2处修饰过度）

📊 总体：局部修复（3个Checker有软问题，无硬伤）

需要修复吗？使用 /novel-studio:revise 10
```

## 与 /novel-studio:revise 的区别

- `/novel-studio:check` = 只检查不修改
- `/novel-studio:revise` = 检查 + 自动修复
