# Setting 目录结构索引（O11 修复）

> **目的**：作为 `setting/` 目录的权威索引模板——初始化新项目时按本表创建文件，让 Architect/Writer/StateManager/Critic 各 Agent 一眼看清每个文件的用途和所有权。
>
> **使用方式**：本文件是**模板**，实际文件写作在工作区的 `setting/` 目录下创建。本文件不复制到工作区，作为 reference/ 中的规范文件供 Agent 查阅。

---

## 目录结构标准

```
setting/
├── 硬规则.yaml              # 不可破坏的规则清单（所有 Agent 强制约束）
├── 系统面板.md              # 系统爽文品类的面板定义（番茄/迪化等）
├── 地点距离表.md            # 地理距离约束（避免地理矛盾，failure-case #45）
├── characters/              # 角色档案
│   ├── 主角.yaml
│   ├── 配角A.yaml
│   └── 配角B.yaml
├── world/                   # 世界规则
│   ├── 时代背景.md
│   ├── 势力分布.md
│   └── 关键地点.md
└── power-system/            # 力量/系统设定（仅在有力量体系的品类）
    ├── 等级体系.md
    └── 修炼规则.md
```

---

## 文件清单与所有权

| 文件/目录 | 所有权 Agent | 写权限 | 读权限 | 用途 |
|----------|-------------|--------|--------|------|
| `setting/硬规则.yaml` | **Architect** | Architect（init 时建，world 时改） | Architect, Writer（约束检查）, Critic（Checker 必检）, StateManager | 全书不可破坏的硬规则——力量上限、地理设定、阵营关系等 |
| `setting/系统面板.md` | **Architect** | Architect（world 时改，writer 时锁） | Writer（写系统时必套用）, Critic（面板一致性检查） | 系统爽文品类的面板定义（字段/标题/数值/格式），锁定后全书唯一权威 |
| `setting/地点距离表.md` | **Architect** | Architect（world 时建/改） | Writer（写地理时检查）, Critic（避免地理矛盾 failure-case #45） | 关键地点之间的距离/方位表 |
| `setting/characters/主角.yaml` | **Architect** | Architect | Writer, Outliner, Critic, StateManager | 主角档案（性格、动机、关系、约束） |
| `setting/characters/配角*.yaml` | **Architect** | Architect（init/world 时建；writer 中新增配角时由 Architect 暂停写作补建） | Writer, Critic, StateManager | 配角档案 |
| `setting/world/` | **Architect** | Architect | Writer（写相关场景）, Outliner（设计情节）, Critic（避免信息矛盾） | 世界规则子目录（时代背景、势力分布、关键地点等） |
| `setting/power-system/` | **Architect** | Architect | Writer, Critic | 力量体系设定（仅在玄幻/仙侠/系统爽文等品类） |

---

## 各 Agent 视角

### Architect（唯一写权限）

- **所有权**：`core/` + `setting/`（含所有子文件）
- **写入时机**：
  - init 时按 `workflow-specs/init-project.md` 流程建骨架
  - world 时按品类配方扩展（番茄系统爽文→系统面板，迪化流→脑补机制设定）
  - writer 中新增重要配角时（`agents/architect.md:70`）暂停写作，Architect 补建角色档案
- **修改限制**：面板锁定后需评估影响，参见 `agents/architect.md:113-118`

### Writer（只读）

- **必读**：`硬规则.yaml`（约束检查）、`系统面板.md`（写系统时必套用）、主角档案（写 POV 时遵循）
- **按需读**：配角档案（写配角 POV 时）、`world/`（写相关场景时）、`地点距离表.md`（写地理时）
- **不能写**：所有 setting/ 文件

### Critic（只读）

- **必读**：`硬规则.yaml`（Checker 必检）、`系统面板.md`（系统爽文品类）、主角/配角档案（人物一致性）
- **按需读**：配角档案、`world/`、`地点距离表.md`
- **触发反馈**：发现 setting 内部矛盾 → 报告 Orchestrator → Orchestrator 决定是否调 Architect 修订

---

## 与其他目录的关系

| 目录 | 关系 |
|------|------|
| `core/作品核心.md` | 上位文件——一句话概括/主角内核/基调由 core 定，setting 按 core 展开 |
| `outline/` | 下游消费方——大纲设定时引用 setting 的角色/世界/力量体系 |
| `chapters/` | 终极消费方——写作时严格遵循 setting 约束 |
| `state/character.yaml` | 镜像 + 运行时状态——`setting/characters/主角.yaml` 是静态档案，`state/character.yaml` 是动态状态（位置/伤势/情绪等） |

---

## 初始化检查清单（新项目）

`/novel-studio:init` 后 Orchestrator 应确认：

- [ ] `setting/硬规则.yaml` 存在（哪怕内容是「待补充」）
- [ ] `setting/characters/主角.yaml` 存在
- [ ] 若品类是系统爽文/迪化流/力量体系相关：`setting/系统面板.md` 存在
- [ ] 若品类含地理信息：`setting/地点距离表.md` 存在
- [ ] `setting/world/` 子目录存在（哪怕只有 README 占位）
- [ ] `setting/power-system/` 子目录存在（按品类决定是否填内容）

---

## 修改触发流（运行时修改 setting）

```
写作者 /novel-studio:write 中
  ↓
Writer 发现需要新配角（例：第 30 章新角色 XX 上场）
  ↓
Writer 暂停 → Orchestrator 调度 Architect 补建角色档案
  ↓
Architect 写入 setting/characters/XX.yaml（按角色档案模板）
  ↓
若该角色引入新规则（例：会某种新魔法）→ 同步更新硬规则.yaml
  ↓
Orchestrator 触发 StateManager 章节事务（character.yaml 加新角色条目）
  ↓
Writer 继续写该 beat
```

**面板修改流**（O11 补充，参考 `agents/architect.md:113-118` 与 A5 观察）：
```
写作者写到第 50 章想改面板字段
  ↓
Orchestrator 暂停写作 → 调度 Architect 评估
  ↓
Architect 评估影响范围（已写章节、即将写章节、Critic 检测项）
  ↓
若 Architect 同意修改 → 同步修改 setting/系统面板.md + 通知 StateManager 更新缓存
  ↓
若涉及已写章节 → 标记为「技术性修订」→ Orchestrator 调度修订流程（/novel-studio:revise）
```

---

## O11 维护说明

本索引由 O11 修复创建于 2026-09，作为 setting 配置目录的权威结构。**未来新增 setting/ 子文件时同步更新本表**（哪个 Agent 写/读、用途、与其他目录的关系）。