# novel-skills

面向中文小说创作的写作 skill 套件。核心目标是帮助作者更稳定地完成正文、保持人物与连续性，并用原文证据提升写作质量。

## 安装

这是一个标准 skills 项目，不需要安装脚本或插件。

1. 下载或克隆本项目。
2. 把 `skills/` 下的每个技能目录放进你的 agent 的 skills 目录，例如 `~/.codex/skills/`。
3. 刷新技能列表后即可按技能名调用。

项目不生成可执行安装器，也不要求把仓库放进特定路径。技能目录本身自包含，复制到目标 skills 目录即可加载。

## 核心原则

- **正文优先**：信息足够时先写，不让资料完整度阻止可逆试写。
- **模式适配**：支持商业连载、类型长篇、文学叙事、短篇和探索起草。
- **人物与因果优先**：连续性、动机、因果、hard canon 和非预期视角漂移是硬门禁。
- **审美目标可选择**：钩子、高潮、字数、对话比例和技法不作为通用质量分数。
- **渐进披露**：只加载当前任务需要的 skill 与参考资料。
- **状态增量**：逐章记录真实变化，周期性合并总账，减少维护对创作的打断。

## 八个核心技能

| 技能 | 职责 |
|---|---|
| novel-studio | 根据当前意图选择最短工作路径 |
| novel-market | 市场研究、对标拆解与商业化包装 |
| novel-project | 最小书核、项目初始化、篇幅与发布约束 |
| novel-worldbuilding | 人物、世界规则、设定与连续性资产 |
| novel-outline | 按模式规划作品、阶段、场景与线索结构 |
| novel-writing | 正文起稿、轻量硬伤检查与状态增量 |
| novel-quality | 证据型体检、最小修订与语言形式校准 |
| novel-feedback | 反馈追踪、假设形成与调整验证 |

## 按意图使用

- 只有一个人物或场景火花：直接使用 `novel-writing` 探索起草。
- 需要规划短篇或长篇结构：使用 `novel-outline` 选择相应深度。
- 续写长篇：先手写或复用最小上下文包，再进入 `novel-writing`。
- 只想审查：使用 `novel-quality`，默认不修改正文。
- 明确需要市场与平台适配：再使用 `novel-market`。

不存在必须完整走完的固定流水线。

## 项目结构参考

```text
my-novel/
├── 00-书核/作品总表.md
├── 10-设定/
├── 20-大纲/
├── 30-正文/
├── 35-参考片段/
└── 90-运行/当前进度.md
```

这是最小参考，不是必须逐项复制的模板。详细目录约定、创建原则与关联见 `skills/novel-project/references/工作区规范.md`。`skills/novel-project/assets/examples/` 提供片段级范例，用来理解每个文件应该承载什么信息，而不是完整工作区脚手架。`35-参考片段/` 是用户自填的段落素材目录，使用规则见 `skills/novel-writing/references/段落参考使用卡.md`。

## 验证

```bash
python3 scripts/validate_skills.py
```

## 参考来源

- [modoojunko/awesome-novel-skill](https://github.com/modoojunko/awesome-novel-skill)
- [leenbj/novel-creator-skill](https://github.com/leenbj/novel-creator-skill)
- [PenglongHuang/chinese-novelist-skill](https://github.com/PenglongHuang/chinese-novelist-skill)
- [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)

## 许可证

Apache-2.0
