---
type: command
name: novel-revise
description: "修订指定章节。根据修订范围跳过部分阶段，最小改动解决指定问题。"
workflow: revise-chapter
---

# /novel revise

修订已完成的章节。根据修订范围选择不同的执行路径。

## 用法

```
/novel revise <章节号>
```

## 修订范围

Orchestrator 会先确认修订范围：

| 你说 | 执行 | 跳过 |
|------|------|------|
| 「重写」「全部重写」 | 完整 write-chapter 流程 | 无 |
| 「节奏不对」「场景有问题」 | ScenePlanner → Writer → Critic | Director |
| 「几处写得不好」「修一下」 | Writer(限制范围) → Critic | Director, ScenePlanner |
| 「AI味太重」「去味」 | Writer(仅修AI味) → Critic(Style only) | Director, ScenePlanner |

## 示例

```
/novel revise 10

[Orchestrator] 修订范围？
→ 场景2的对话太生硬了，第3段有AI味

🔧 局部修复模式：2处对话 + 1处AI味

📝 修复完成（+80字，<5%）
🔍 复查通过

📋 第10章已更新
```

## 强制规则

- 修订后字数波动不超过 ±20%（除非用户明确要求扩写/缩写）
- 修订不能改变章节的硬设定
- 修订不能新增未授权的信息释放
- 如果修复引发新硬伤 → 自动升级修订范围
