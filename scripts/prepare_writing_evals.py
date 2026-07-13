#!/usr/bin/env python3
"""校验并生成不泄露隐藏检查项的写作评测包。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "skills" / "novel-writing" / "assets" / "evals" / "writing-cases.json"
MODES = {"商业连载", "类型长篇", "文学叙事", "短篇", "探索起草"}
REQUIRED = {"id", "mode", "task", "context", "must_preserve", "failure_signals"}


def load_cases(path: Path) -> list[dict]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("评测清单必须是非空数组")
    seen: set[str] = set()
    for case in cases:
        missing = REQUIRED - set(case)
        if missing:
            raise ValueError(f"评测项缺少字段: {sorted(missing)}")
        if not re.fullmatch(r"[a-z0-9-]+", case["id"]):
            raise ValueError(f"非法评测 id: {case['id']}")
        if case["id"] in seen:
            raise ValueError(f"重复评测 id: {case['id']}")
        if case["mode"] not in MODES:
            raise ValueError(f"未知写作模式: {case['mode']}")
        if not case["must_preserve"] or not case["failure_signals"]:
            raise ValueError(f"评测项必须包含保留项和失败信号: {case['id']}")
        seen.add(case["id"])
    return cases


def prompt_packet(case: dict) -> str:
    return (
        f"# 写作任务：{case['id']}\n\n"
        f"写作模式：{case['mode']}\n\n"
        f"## 上下文\n\n{case['context']}\n\n"
        f"## 任务\n\n{case['task']}\n\n"
        "直接输出正文。不要输出分析、检查表或写作说明。\n"
    )


def evaluator_packet(case: dict) -> str:
    preserve = "\n".join(f"- {item}" for item in case["must_preserve"])
    failures = "\n".join(f"- {item}" for item in case["failure_signals"])
    return f"""# 评审卡：{case['id']}

先盲读候选正文，再查看本卡。每项 1-5 分，并引用候选原文。

## 共同维度

- 写作模式与任务匹配
- 人物真实与选择可信
- 视角和信息控制
- 语言、形式与节奏有效
- 连续性与约束保持

## 必须保留

{preserve}

## 失败信号

{failures}

## 结论

- 最有效的原文证据：
- 最影响阅读效果的问题：
- 最小修改建议：
- 是否值得进入下一轮：是 / 否 / 需作者判断
"""


def prepare(cases: list[dict], output: Path) -> None:
    prompts = output / "prompts"
    scorecards = output / "scorecards"
    prompts.mkdir(parents=True, exist_ok=True)
    scorecards.mkdir(parents=True, exist_ok=True)
    for case in cases:
        (prompts / f"{case['id']}.md").write_text(prompt_packet(case), encoding="utf-8")
        (scorecards / f"{case['id']}.md").write_text(evaluator_packet(case), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="准备写作 Skill 的盲评任务包")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="评测清单 JSON")
    parser.add_argument("--output", help="输出目录；省略时只校验")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        cases = load_cases(Path(args.manifest).expanduser().resolve())
        if args.output:
            prepare(cases, Path(args.output).expanduser().resolve())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    action = "已生成" if args.output else "校验通过"
    print(f"写作评测清单{action}：{len(cases)} 个任务，覆盖 {len({case['mode'] for case in cases})} 种模式")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
