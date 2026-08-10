# novel-studio 升级计划

## 已完成变更

### 1. 工作区目录英文化
| 旧 | 新 |
|----|----|
| `00-书核/` | `core/` |
| `10-设定/` | `setting/` |
| `20-大纲/` | `outline/` |
| `30-正文/` | `chapters/` |
| `35-参考片段/` | `snippets/` |
| `90-状态/` | `state/` |
| `归档/` | `archive/` |
| `角色/`（路径） | `characters/` |
| `分卷/` | `volumes/` |
| `世界观/` | `world/` |
| `力量体系/` | `power-system/` |

### 2. 选择性 YAML 化
| 文件 | 格式 |
|------|------|
| `core/作品总表` | MD |
| `setting/硬设定` | **YAML** |
| `setting/characters/*` | **YAML** |
| `setting/world/*` | MD |
| `setting/power-system/*` | MD |
| `outline/全书总纲` | MD |
| `outline/volumes/*` | **YAML** |
| `chapters/*` | MD |
| `state/*` | YAML（已是） |

### 3. 移除伏笔账本
`state/foreshadow.yaml` 作为唯一伏笔追踪源。

### 4. install.sh
一行安装：`sh https://raw.githubusercontent.com/deathwhispers/novel-studio/main/install.sh`

从 GitHub raw URL 下载 agents/commands/skills 到 `~/.claude/`。

### 5. 项目目录结构不变
agents/、commands/、skills/ 保持在根目录。
