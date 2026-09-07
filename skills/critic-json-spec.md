# Critic 输出 JSON 规范

目的：规定 Critic 返回的结构化检查结果，便于自动化流水线决策与 Writer 接受建议。

示例结构：
```json
{
  "panel_consistent": true,
  "leaks": [],
  "pacing_score": 7,
  "conflicts": [
    {"loc": "para2", "desc": "外部阻碍弱，建议增加对手干预"}
  ],
  "sensory_density": 3,
  "repetition_rate": 8.2,
  "suggested_changes": [
    {"loc":"para1","change":"替换说明句为行为展现"}
  ]
}
```

规则说明：
- `panel_consistent`：若为 false，必须包含 `leaks`（列出不一致句子与修正建议）。
- `pacing_score`：0-10（低于 5 触发重写建议）。
- `suggested_changes`：每项应包含 `loc` 与 `change`，并尽量给出替代表述。
