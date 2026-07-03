# 部署指南

novel-skills 支持多种 AI 工具的便捷部署。本指南涵盖 3 种主流工具的安装、使用、卸载。

## 支持的工具

| 工具 | 检测命令 | 安装命令 | 配置文件 |
|------|---------|---------|---------|
| **Codex CLI** (OpenAI) | `codex --version` | `python3 scripts/install.py --target codex` | `~/.codex/config.toml` |
| **Claude Code** (Anthropic) | `claude --version` | `python3 scripts/install.py --target claude` | `~/.claude/settings.json` |
| **OpenCode** (开源) | `opencode --version` | `python3 scripts/install.py --target opencode` | `~/.config/opencode/config.json` |

## 快速开始

### 1. 自动检测并安装

```bash
python3 scripts/install.py
```

脚本会：
- 检测已安装的工具
- 列出检测结果
- 提示选择安装目标
- 自动复制和配置

### 2. 指定工具安装

```bash
# 只安装到 Codex
python3 scripts/install.py --target codex

# 安装到 Claude Code
python3 scripts/install.py --target claude

# 安装到 OpenCode
python3 scripts/install.py --target opencode

# 全部安装（仅在多工具共存时）
python3 scripts/install.py --target all
```

### 3. 仅复制 skills/ 目录

如果你的工具是自定义的，或者你想手动管理 plugins，可以只复制 skills/ 目录：

```bash
python3 scripts/install.py --skills-only --target-dir /path/to/your/project
```

复制后，把 `novel-skills/` 目录中的 skills 目录放到你工具期望的位置。

## 各工具的详细安装

### Codex CLI

**前置条件**：
- 已安装 Codex CLI（[官方安装](https://github.com/openai/codex)）
- `~/.codex/` 目录可写

**安装步骤**：

```bash
python3 scripts/install.py --target codex
```

**做了什么**：
1. 复制 `~/.codex/plugins/cache/novel-local/novel-skills/<version>/`
2. 注册 marketplace 到 `~/.codex/marketplaces/novel-local/`
3. 更新 `~/.codex/config.toml`：
   - 添加 `[features] plugins = true`
   - 添加 `[plugins] enabled = ["novel-skills@novel-local"]`

**使用方法**：
- 重启 Codex CLI
- 开新 thread
- 输入：`用 novel-studio 帮我判断下一步该走哪个 skill`
- 或者直接调用：`$novel-bootstrap`、`$novel-drafting` 等

**卸载**：

```bash
python3 scripts/install.py --target codex --uninstall
```

或者：

```bash
python3 scripts/install.py --uninstall  # 全部卸载
```

### Claude Code

**前置条件**：
- 已安装 Claude Code（[官方安装](https://claude.com/claude-code)）
- `~/.claude/` 目录可写

**安装步骤**：

```bash
python3 scripts/install.py --target claude
```

**做了什么**：
1. 复制到 `~/.claude/plugins/novel-skills/`
2. 复制 `.claude-plugin/` 目录（plugin.json + commands/）
3. 复制 `skills/` 目录
4. 更新 `~/.claude/settings.json`：
   - 添加 `"plugins": { "novel-skills": { "enabled": true, "path": "..." } }`

**使用方法**：
- 重启 Claude Code
- 在输入框输入 `/novel` 启动工作台
- 或者输入 `/novel-init` 初始化项目
- 或者输入 `/novel-checkup` 做章节体检
- 或者输入 `/novel-roleplay` 角色扮演

**可用的 commands**：
- `/novel` - 启动工作台（路由到具体 skill）
- `/novel-init` - 初始化项目
- `/novel-checkup` - 章节体检
- `/novel-validate` - 项目结构校验
- `/novel-roleplay` - 角色扮演

**卸载**：

```bash
python3 scripts/install.py --target claude --uninstall
```

### OpenCode

**前置条件**：
- 已安装 OpenCode
- `~/.config/opencode/` 目录可写

**安装步骤**：

```bash
python3 scripts/install.py --target opencode
```

**做了什么**：
1. 复制 skills/ 到 `~/.config/opencode/skills/novel-skills/`
2. 复制 commands/ 到 `~/.config/opencode/commands/novel-skills/`
3. 复制 agents/ 到 `~/.config/opencode/agents/novel-skills/`

**使用方法（方式一：作为全局插件）**：
- OpenCode 会自动发现 `~/.config/opencode/` 下的 skills/、commands/、agents/
- 在任意项目中输入 `/novel` 启动

**使用方法（方式二：在项目内直接打开）**：
```bash
cd /path/to/novel-skills
opencode
```
OpenCode 会自动读取项目根目录的 `opencode.json`、`skills/`、`.opencode/commands/`。

**卸载**：

```bash
python3 scripts/install.py --target opencode --uninstall
```

## 不安装任何插件：直接使用 skills/ 目录

如果你的工具不在这 3 种之内，或者你想手动管理，可以直接复制 skills/ 目录：

```bash
# 复制到任意位置
python3 scripts/install.py --skills-only --target-dir /tmp

# 然后手动把 skills/novel-skills/ 复制到你的工具期望的位置
# 例如：~/.config/your-tool/skills/novel-skills/
```

或者直接 `cp -R skills/ /path/to/your-tool/skills/`。

## 项目结构说明

安装后，你的工具会看到以下 skills：

```
your-tool/
├── skills/                  # 自动发现
│   └── novel-skills/        # 来自本项目
│       ├── novel-studio/    # 路由 skill
│       ├── novel-bootstrap/ # 开书建档
│       ├── novel-worldbuilding/  # 设定总表
│       ├── novel-outlining/  # 铺线列纲
│       ├── novel-drafting/  # 写章起稿
│       ├── novel-checkup/   # 体检
│       ├── novel-revision/  # 修订
│       ├── novel-ideation/  # 立项
│       ├── novel-market-scan/   # 扫榜
│       ├── novel-deconstruction/  # 拆文
│       ├── novel-commercial-writing/  # 商业化
│       ├── novel-deslop/    # 去 AI 味
│       ├── novel-volumning/  # 卷纲
│       └── novel-ai-writing/  # AI 协作
```

## 测试安装

安装后，**新开一个 thread/对话**，输入：

### Codex
```
用 novel-studio 帮我判断下一步该走哪个 skill。
```

### Claude Code
```
/novel
```

### OpenCode
```
/novel
```

## 卸载所有

```bash
python3 scripts/install.py --uninstall
```

这会从所有已安装的工具中移除 novel-skills。

## 常见问题

### Q: 安装后没有效果？

**A**: 大部分工具需要**重启**才能加载新插件。重启后**新开一个 thread/对话**测试。

### Q: 可以同时安装到多个工具吗？

**A**: 可以。`python3 scripts/install.py --target all` 会同时安装到所有已检测到的工具。各个工具独立，互不影响。

### Q: 安装后更新版本？

**A**: 重新运行 `python3 scripts/install.py --target <tool>` 即可。会自动覆盖旧版本。

### Q: 不想用脚本怎么办？

**A**: 直接复制本项目到你工具的 skills/ 目录即可。详细说明见上文的"不安装任何插件"部分。

### Q: skills-only 模式和完整安装模式的区别？

**A**: 
- **skills-only**：只复制 `skills/` 目录到目标位置，需要你手动配置工具
- **完整安装**：自动配置工具的 plugins/skills 目录、settings.json、commands/ 等

### Q: 如何让多本书复用同一份 skills？

**A**: 安装到全局目录（如 `~/.codex/plugins/`、`~/.claude/plugins/`）即可。所有项目都能用同一份 skills。

## 高级：自定义安装路径

如果你想安装到非默认位置：

```bash
# 把 skills/ 复制到自定义目录
python3 scripts/install.py --skills-only --target-dir /path/to/dir
```

然后在 `path/to/dir/novel-skills/` 中找到 `skills/` 目录，按需使用。

## 高级：更新版本

```bash
# 拉取最新代码
git pull

# 重新安装
python3 scripts/install.py

# 或指定工具
python3 scripts/install.py --target codex
```

## 高级：开发/调试模式

如果你在开发 skills 本身：

```bash
# 把项目目录作为 skills 目录软链接到工具配置
ln -s /path/to/novel-skills/skills /path/to/your-tool/skills/novel-skills

# 修改 skills 后立即生效，无需重装
```

## 反馈

部署过程中遇到问题？[提交 issue](https://github.com/wh1sp3rrr/novel-skills/issues)
