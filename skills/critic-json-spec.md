# Critic 输出 JSON 规范（⚠️ 早期草案，不推荐使用）

> **状态：早期草案 / 简化版本**——Orchestrator 不解析此格式，Writer 收到的"建议修改"以 `agents/critic.md` 的 YAML `review_report` / `lite_report` 为权威。
>
> **O4 修复（2026-09）**：本规范与 `agents/critic.md` 的输出格式不一致（前者 JSON、后者 YAML）。统一以 `agents/critic.md` YAML 格式为权威输出。本文件保留作为历史参考和外部工具集成场景的简化对接入口，**不要**在 Orchestrator/Writer 内部使用本格式。
>
> 若未来需要 JSON 输出，建议重写一份 critic 输出的 YAML→JSON 转换器（schema 同步 `agents/critic.md` 的 YAML 字段），而不是维护两套并行 schema。

---

## 历史版本内容

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

**已知不一致**（O4 修复背景）：
- 字段命名：`loc`（JSON） vs `location`（YAML）；`change`（JSON） vs `fix`/`fix_suggestions`（YAML）
- 覆盖面：JSON 版本只覆盖 6 项（panel/leaks/pacing/conflicts/sensory/repetition）；YAML 版本覆盖 5 checker + verdict + required_actions + cannot_fix_locally
- 评分维度：JSON 用 `pacing_score` 0-10；YAML 用 issues 数组 + severity 字段
