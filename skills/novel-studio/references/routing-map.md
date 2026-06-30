# 路由地图

## 常见用户表达 -> skill

- “帮我开一本新书” -> `novel-bootstrap`
- “我有个脑洞，帮我整理一下” -> `novel-ideation`
- “帮我补人物设定/世界观” -> `novel-worldbuilding`
- “帮我拆成分卷和章节” -> `novel-outlining`
- “帮我检查这章顺不顺、前后有没有打架” -> `novel-checkup`
- “继续写下一章” -> `novel-drafting`
- “这章太 AI 了，帮我重写” -> `novel-revision`

## 跨阶段请求

- “从脑洞做到第一卷大纲”
  - 先 `novel-ideation`
  - 再 `novel-worldbuilding`
  - 再 `novel-outlining`

- “把旧稿整理好再继续写”
  - 先 `novel-bootstrap`
  - 再根据缺口转 `novel-worldbuilding` 或 `novel-outlining`
  - 最后 `novel-drafting`

- “我这一章写完了，先帮我查问题再修”
  - 先 `novel-checkup`
  - 再转 `novel-revision`
