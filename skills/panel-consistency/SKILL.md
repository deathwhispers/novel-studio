# Panel Consistency SKILL

目的：核对文本与 `setting/系统面板.md` 中的字段是否一致，检测未授权面板变更。

输入：文本、当前 `panel`（YAML 片段）。

输出：`panel_consistent` 布尔、`leaks` 列表、如有 `panel_patch` 建议。

样例 Prompt：
"核对下面文本是否与给定 panel 一致。若发现不一致，列出具体句子并给出替换句；若文本应修改 panel，返回 `panel_patch`（字段、old->new、理由）。"
