---
description: 对当前章节做体检（连续性/前后照应/信息债/章尾/伏笔）
allowed-tools: Read, Bash
---

# 小说章节体检

为用户对当前章节做体检，并输出一份问题清单。

## 体检流程

1. 读取 `90-运行/当前进度.md` 确认当前章节
2. 读取当前章节正文 + 上一章最后段落 + 节拍卡
3. 按以下 6 层检查：
   - 本章是否站得住
   - 前后衔接是否顺
   - 埋线与回收
   - 人物状态
   - 章尾发动机
   - 追读即时风险
4. 输出按 P0/P1/P2 排序的问题清单
5. 建议转给哪个 skill 处理：
   - 结构错位 → `novel-outlining`
   - 设定冲突 → `novel-worldbuilding`
   - 正文修复 → `novel-revision`

## 详细模板

参考 `skills/novel-checkup/references/章节体检模板.md`。
