---
name: novel-worldbuilding
description: "中文小说设定圣经 skill。用于构建或修订人物档案、世界规则、地点、势力、时间线、母题系统和 hard canon，尤其适合长篇连载需要稳定连续性的场景。适用于“帮我补世界观”“整理角色关系”“建立设定圣经”“修复设定冲突”“给这本书做人物档案”等请求。"
---

# 设定总表

## 功能定位

把创意变成可以长期复用的设定资产。所有设定都应服务剧情与角色，而不是为了炫耀百科知识。

## 核心原则

1. 先冲突，后设定
2. 先 hard canon，后柔性补充
3. 人物优先于世界说明
4. 每次新增设定都要能回答“它会影响什么剧情或选择”

## 主要产物

- `10-bible/canon.md`
- `10-bible/world-rules.md`
- `10-bible/地点.md`
- `10-bible/势力.md`
- `10-bible/时间线.md`
- `10-bible/母题.md`
- `10-bible/角色/*.md`

## 人物文件最低要求

每个主要角色至少要有：

- role
- desire
- fear
- contradiction
- secret
- leverage
- voice markers
- relationship pressure
- arc direction

## 变更规则

- 如果修订了 hard canon，同步在 `90-ops/decisions.md` 记录原因。
- 如果只是补充 flavor text，不要伪装成 hard canon。
- 如果用户要求“随便补一点设定”，优先补会影响当前大纲或下一章的设定。

## 资源

需要更细的字段或边界时，读取 `references/story-bible-map.md`。
