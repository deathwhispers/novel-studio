---
type: command
name: check
description: "对指定章节做质量检查。先确认你关心什么，再定向检查，不修改正文。"
workflow: check
---

# /novel-studio:check

对已完成的章节做质量检查。**不直接全量扫描**——先问你想关注什么，再有针对性地查。

## 核心原则

- **定向优先**：先知道你在担心什么，再决定检查重点
- **不过度诊断**：你说只看 AI 味，就不跑完整 5 个 Checker
- **只报问题，不给方案**：check 只诊断，不修改。修改用 `/novel-studio:revise`

## 用法

```
/novel-studio:check <章节号>
/novel-studio:check               # 检查最新完成的章节
```

## 对话流程

### 第一步：确认检查范围

```
🔍 检查第 N 章。你想重点看什么？

（可以直接说，比如：
- 「全部过一遍」
- 「主要看有没有 AI 味」
- 「角色有没有崩」
- 「节奏对不对」
- 「有没有泄露不该说的信息」
- 或者描述你读完后觉得不对的地方）
```

等待用户回答。

### 第二步：定向检查

根据用户的选择，只运行相关的 Checker：

| 用户关心的 | 运行的 Checker |
|-----------|---------------|
| 「全部过一遍」 | 5 个 Checker 全部 |
| 「AI 味 / 文风 / 写得僵」 | Style Checker（重点）+ Pace Checker（辅助） |
| 「角色有没有崩 / 人设」 | Character Checker + Logic Checker |
| 「节奏 / 太拖 / 太快」 | Pace Checker + Logic Checker |
| 「信息控制 / 泄露」 | Info Leak Checker + Logic Checker |
| 「逻辑 / 情节 bug」 | Logic Checker |
| 「读着不舒服但说不上来」 | Style Checker → Character Checker → Pace Checker（逐步） |

### 第三步：报告

只报告发现的问题，不输出通过的 Checker（除非用户说「全部过一遍」）：

```
🔍 第 N 章检查结果（按你说的，重点看 AI 味和角色）：

   ⚠️ AI 味：4 处
      - 场景 1，第 2 段：「他感到一阵紧张」→ 解释腔
      - 场景 2，对话：「不是我不帮你，而是...」→ 否定句式
      - 场景 2，第 4 段：「第一...第二...」→ 机械罗列
      - 场景 3，第 1 段：连续 300 字全视觉描写 → 活人感缺失

   ⚠️ 角色：1 处
      - 场景 2：配角 XX 的行为缺少动机——突然帮忙很奇怪

   📊 没有硬伤，6 处软问题。

需要修复的话：/novel-studio:revise N
```

## 与 /novel-studio:revise 的区别

- `/novel-studio:check` = 诊断，不治疗。先看看有什么问题
- `/novel-studio:revise` = 诊断 + 治疗。检查后直接修复

## 反模式（禁止）

见 `workflows/check.md` 的反模式段。
