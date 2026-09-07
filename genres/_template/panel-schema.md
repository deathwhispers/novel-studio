# 系统面板模式（panel_schema）

目的：统一每本书的系统字段与写法，供 `Init` 步骤实例化到 `setting/系统面板.md`。

示例 YAML 模板：
```yaml
name: "主系统名称"
version: 1
fields:
  - key: level
    type: integer
    initial: 1
    upgrade_rule: "经验>=100 -> +1"
  - key: power
    type: integer
    initial: 10
    upgrade_rule: "按任务获得"
  - key: hidden_ability
    type: string
    initial: null
    reveal_condition: "触发第10次任务或特定剧情节点"
rewards:
  - type: currency
    name: coin
    rules: "任务奖励/签到/商城兑换"
change_log: []
```

说明：任何写稿触发的面板改动必须以 `panel_patch` 形式返回并记录到 `change_log`。
