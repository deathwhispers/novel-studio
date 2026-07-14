# novel-skills

面向中文小说创作的写作 skill 套件。核心目标是帮助作者更稳定地完成正文、保持人物与连续性，并用可验证证据提升写作质量。

## 核心原则

- **正文优先**：信息足够时先写，不让资料完整度阻止可逆试写。
- **模式适配**：支持商业连载、类型长篇、文学叙事、短篇和探索起草。
- **人物与因果优先**：连续性、动机、因果、hard canon 和非预期视角漂移是硬门禁。
- **审美目标可选择**：钩子、高潮、字数、对话比例和技法不作为通用质量分数。
- **渐进披露**：只加载当前任务需要的 skill 与参考资料。
- **状态增量**：逐章记录真实变化，周期性合并总账，减少维护对创作的打断。

## 快速开始

查看 [QUICKSTART.md](QUICKSTART.md)。

初始化示例：

```bash
python3 skills/novel-project/scripts/init_novel_project.py \
  --output /path/to/my-novel \
  --title "书名" \
  --genre "题材" \
  --premise "一句话故事前提" \
  --profile minimal \
  --mode 探索起草
```

模板档位控制资料脚手架：

- `minimal`：短篇、文学叙事、试写和轻量项目。
- `serial`：常规项目资料深度。
- `longform`：复杂势力、多主角或超长篇。

模板档位不等于写作模式。例如文学长篇可以使用 `longform` 资料档位，同时保持“文学叙事”质量目标；这时不会生成连载驾驶舱、留存表和首卷发射台。商业连载模式会自动启用这组工具；其他模式如需分章发布管理，显式传入 `--enable-serial-tools`。启停状态会写入 `90-运行/项目配置.md`。

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
- 续写长篇：先生成最小上下文包，再进入 `novel-writing`。
- 只想审查：使用 `novel-quality`，默认不修改正文。
- 明确需要市场与平台适配：再使用 `novel-market`。

不存在必须完整走完的固定流水线。

## 工具

生成续写上下文包：

```bash
python3 scripts/build_context_pack.py /path/to/my-novel \
  --chapter 12 \
  --task "沈砚回到旧屋，与妹妹谈昨夜的债主" \
  --output /path/to/my-novel/90-运行/context-chapter-012.md
```

扫描表层文本风险（不输出文学质量综合分）：

```bash
python3 scripts/evaluate_chapter.py /path/to/my-novel \
  --chapter 第012章 \
  --profile auto
```

生成隔离的盲评包：

```bash
python3 scripts/prepare_writing_evals.py \
  --writer-output /tmp/novel-writer-bundle \
  --evaluator-output /tmp/novel-evaluator-bundle
```

两个目录应分别交给写作者和评审者，不能让写作者看到评审包中的隐藏失败信号。

## 项目结构

```text
my-novel/
├── 00-书核/       # 写作模式、意图与作品承诺
├── 05-市场/       # 明确需要商业研究时使用
├── 10-设定/       # 人物、世界、hard canon 与 voice
├── 20-大纲/       # 作品、阶段、写作支点、因果与线索
├── 30-正文/       # 正文
├── 40-修订/       # 深度体检或实际修订记录
├── 50-归档/
└── 90-运行/       # 当前进度、项目配置、状态增量与训练日志
```

## 验证

```bash
python3 scripts/validate_skills.py
python3 -m unittest discover -s tests -v
```

## 参考来源

- [modoojunko/awesome-novel-skill](https://github.com/modoojunko/awesome-novel-skill)
- [leenbj/novel-creator-skill](https://github.com/leenbj/novel-creator-skill)
- [PenglongHuang/chinese-novelist-skill](https://github.com/PenglongHuang/chinese-novelist-skill)
- [worldwonderer/oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode)

## 许可证

Apache-2.0
