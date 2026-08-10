---
type: workflow
name: revise-chapter
description: "章节修订流程。根据修订范围跳过部分阶段，目标是最小改动解决指定问题。"
---

# revise-chapter — 章节修订 Workflow

## 状态机

```
用户: /novel revise <chapter>
            │
            ▼
    Orchestrator: 确认修订范围
            │
            ├── 全文重写 → 完整 write-chapter 流程
            ├── 场景重设 → ScenePlanner → Writer → Critic → StateManager
            ├── 局部修复 → Writer(限制范围) → Critic → StateManager
            └── 仅去味   → Writer(仅修AI味) → Critic(Style Checker only) → StateManager
```

## 修订范围判断

Orchestrator 通过多轮确认判断修订范围：

| 用户说 | 修订范围 | 跳过 |
|--------|---------|------|
| 「重写第X章」「全部重写」 | 全文重写 | 无 |
| 「第X章节奏不对」「场景结构有问题」 | 场景重设 | Director |
| 「有几处写得不好」「对话修一下」 | 局部修复 | Director, ScenePlanner |
| 「AI味太重」「去味」 | 仅去味 | Director, ScenePlanner |

## 各修订范围流程

### 全文重写

```
Director → ScenePlanner → Writer → Critic → StateManager
（等同于 write-chapter，不优化）
```

### 场景重设

```
ScenePlanner（重新设计 Scene Contract，保持 Story Contract 不变）
    ↓
Writer（按新 Scene Contract 重写）
    ↓
Critic（完整 5 Checker）
    ↓
StateManager（更新状态）
```

### 局部修复

```
Writer（只修 Critic 标记的问题项，不重写全文）
    ↓
Critic（只重新检查标记项相关的 Checker）
    ↓
StateManager（更新状态）
```

Writer 在局部修复模式的约束：
- 不改动未标记的场景和段落
- 修复后保持前后文的连贯性
- 如果修复牵涉超过 30% 的正文 → 升级为场景重设

### 仅去味

```
Writer（全文搜索 AI 味关键词 → 逐项修复 → 不改动剧情/结构/角色）
    ↓
Critic（仅 Style Checker）
    ↓
StateManager（更新状态）
```

## 强制规则

1. **修订后的字数波动不超过 20%**（除非用户要求扩写/缩写）
2. **修订不能改变章节的硬设定**（不能突然改了力量等级或角色关系）
3. **修订不能新增未在 Story Contract 中允许的信息**
4. **如果修复引发新的硬伤 → 升级修订范围**

## 用户可见输出

```
🔧 正在修订第10章（局部修复：3处对话 + 2处AI味）

📝 修复完成：
   ✅ 场景2对话：增加了主角和被救者之间的张力
   ✅ 场景3结尾：删除了「在这一刻」等AI味表达
   ✅ 5处修改，字数变化 +120 字（<5%）

🔍 复查中…
✅ 修复项全部通过，无新增问题
```
