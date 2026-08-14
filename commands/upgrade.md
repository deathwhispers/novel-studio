---
type: command
name: upgrade
description: "旧版工作区升级。将 v2 旧结构无损升级到 v3，保留 state/ 续写上下文。"
workflow: upgrade-project
---

# /novel-studio:upgrade

将已经在写作中的旧版 novel-studio 项目升级到当前结构。只改文件名和 progress.yaml 字段，**不重扫正文、不重建状态**，角色/读者/伏笔/作者秘密全部保留。

## 用法

```
/novel-studio:upgrade
```

在当前工作区目录下执行。Orchestrator 会自动检测是否旧版，是则进入升级流程。

## 执行流程

1. **检测 + 确认**：识别旧版特征（`core/作品总表.md` 存在 / progress.yaml 用 `hard_canon` / 缺 `schema_version`），展示升级清单
2. **备份**：progress.yaml + core/ + setting/ 快照到 `_upgrade-backup/`，可回滚
3. **结构改名**：作品总表→作品核心、硬设定→硬规则、progress.yaml 字段改写
4. **内容补全**：Architect 补 core 灵魂契约（缺失字段请作者补充）+ 拆硬设定（力量/身份归位）
5. **校验收尾**：确认无残留旧路径，写入 `schema_version: 3`

## 示例

```
/novel-studio:upgrade

🔍 检测到旧版工作区（v2），需升级到 v3。
   升级前会先备份到 _upgrade-backup/。

💾 备份完成…
🔧 结构改名完成：
   core/作品总表.md  → core/作品核心.md
   setting/硬设定.yaml → setting/硬规则.yaml

💬 core 灵魂契约补全：
   已自动迁移 3 项，待你补充 2 项（基调 / 禁忌与红线）…

✅ 升级完成！state/ 全部状态已保留，可继续续写。
```

## 注意事项

- 升级是**结构迁移**，不会重写已写章节，也不会重建角色/伏笔状态
- `state/` 下 author/reader/character/foreshadow 一律不动，续写上下文完整保留
- 升级前自动备份，确认无误后删除 `_upgrade-backup/`
