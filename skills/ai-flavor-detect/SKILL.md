---
name: ai-flavor-detect
description: "AI 味检测。搜索全文中的 AI 味关键词和模式，标记位置和类型。纯能力，由 Writer（自检）和 Critic（正式扫描）共同调用。"
category: analysis
---

# AI 味检测

> AI 味不是禁用词表，而是语言选择与人物、场景和叙事目的脱节。本 skill 只做检测和标记，不自动修改——修改由 Writer 执行。

## 检测流程

### 步骤 1：关键词扫描 + 结构扫描

按 `references/ai-flavor-checklist.md` 逐项执行（24 项关键词扫描 + 9 项结构扫描）。不在此重复关键词表。

### 步骤 2：角色声音检查

- [ ] 不同角色的对话去掉标签后能否分辨？
- [ ] 是否存在所有角色都用相似句式的情况？
- [ ] 是否存在「安全表达」——回避强烈、有风险的说法？

## 输出格式

```yaml
ai_flavor_report:
  total_hits: 6
  by_category:
    解释腔: 2
      - location: "第3段"
        text: "他感到一阵愤怒"
        suggestion: "改为：他握紧拳头，指节发白"
      - location: "第12段"
        text: "她意识到自己犯了一个错误"
        suggestion: "改为：她的手停在半空。完了。"
    修饰过度: 2
      - location: "第5段"
        text: "她轻轻叹了口气，缓缓转过身"
        suggestion: "删掉'轻轻''缓缓'，或只保留一个"
    模板化句式: 1
      - location: "第8段"
        text: "他深吸一口气，缓缓说道"
        suggestion: "直接写对话：'我去。'"
    陈旧意象: 1
      - location: "第14段"
        text: "空气仿佛凝固了"
        suggestion: "改为具体的人物反应——谁做了什么/没做什么"
  structural_issues: []
  voice_issues: []
```

## 阈值与行动

见 `references/ai-flavor-checklist.md` 的检测阈值。

## 核心原则

- **不是禁词表**：「他感到冷风灌进来」是正常描写，「他感到恐惧」才是 AI 味
- **改后要更像角色**：如果去味后的句子不像这个角色 → 回退
- **不要为了去味而去味**：重点是效果受损，不是规则合规
