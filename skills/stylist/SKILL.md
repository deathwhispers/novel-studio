---
name: stylist
description: "修订阶段专用润色 skill。把文本从说明式改为展现式，提升语言质感。**仅由 Orchestrator 在修订场景（/novel-studio:revise）调起，不被 Writer 在 beat 起草阶段直接调**。"
category: revision
---

# Stylist SKILL（修订场景专用，O10 修复）

目的：在不改变核心信息点与面板的前提下，把文本从说明式改为展现式，提升语言质感与可读性。

## 调用方（O10 修复）

| 阶段 | 是否调本 skill |
|------|--------------|
| 写章节 beat 起草（Writer 主动） | ❌ **不调**——起草阶段用 `description`（描写技法）+ `scene-render`（场景渲染） |
| 修订章节（`/novel-studio:revise`，Orchestrator 调度） | ✅ **由 Orchestrator 调度 Writer 调用**——整章或局部润色 |
| 写后微调（用户说"这段可以再润色一下"） | ✅ 由 Writer 调，但应建议走 `/novel-studio:revise` |

**为什么起草阶段不调**：本 skill 是"修订视角"——已经写完的文本如何润色。起草阶段文笔尚未定型，过早润色会浪费工时。

输入：文本、目标风格说明（如：直白、细腻、幽默）。

输出：修改后文本、`edits` 列表（每项包含原句、改写句与改动理由）。

示例 Prompt：
"在不改变剧情信息的前提下润色以下文本：1) 把说明句改为展现句；2) 增加至少两处感官细节；3) 替换重复词。返回修改后文本与 `edits` 注记。"

## 边界（O10 修复）

| 关注 | 在哪里 |
|------|--------|
| 写得好不好看（说明式→展现式润色） | **本 skill**（仅修订场景） |
| 怎么写（先印象后细节、特征化） | `description` |
| 声音统一不漂移（叙述者声音锁定） | `style-calibrate` |
| 检测"眼中闪过一丝复杂"等 AI 句式 | `ai-flavor-detect` |
