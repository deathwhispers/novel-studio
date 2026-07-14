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
DIFFICULTIES = {"standard", "adversarial"}
REQUIRED = {
    "id", "mode", "difficulty", "capabilities", "task", "context",
    "must_preserve", "failure_signals",
}


def load_cases(path: Path) -> list[dict]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("评测清单必须是非空数组")
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("每个评测项必须是对象")
        missing = REQUIRED - set(case)
        if missing:
            raise ValueError(f"评测项缺少字段: {sorted(missing)}")
        if not isinstance(case["id"], str) or not re.fullmatch(r"[a-z0-9-]+", case["id"]):
            raise ValueError(f"非法评测 id: {case['id']}")
        if case["id"] in seen:
            raise ValueError(f"重复评测 id: {case['id']}")
        if not isinstance(case["mode"], str) or case["mode"] not in MODES:
            raise ValueError(f"未知写作模式: {case['mode']}")
        if case["difficulty"] not in DIFFICULTIES:
            raise ValueError(f"未知评测难度: {case['id']}: {case['difficulty']}")
        if not all(isinstance(case[field], str) and case[field].strip() for field in ("task", "context")):
            raise ValueError(f"任务和上下文必须是非空字符串: {case['id']}")
        list_fields = ("capabilities", "must_preserve", "failure_signals")
        if not all(isinstance(case[field], list) and case[field] for field in list_fields):
            raise ValueError(f"评测项必须包含能力、保留项和失败信号: {case['id']}")
        if not all(isinstance(item, str) and item.strip() for field in list_fields for item in case[field]):
            raise ValueError(f"能力、保留项和失败信号必须是非空字符串: {case['id']}")
        if len(case["capabilities"]) != len(set(case["capabilities"])):
            raise ValueError(f"能力标签不得重复: {case['id']}")
        seen.add(case["id"])
    return cases


def prompt_packet(case: dict) -> str:
    preserve = "\n".join(f"- {item}" for item in case["must_preserve"])
    capabilities = "、".join(case["capabilities"])
    return (
        f"# 写作任务：{case['id']}\n\n"
        f"写作模式：{case['mode']}\n\n"
        f"任务难度：{case['difficulty']}\n\n"
        f"能力焦点：{capabilities}\n\n"
        f"## 上下文\n\n{case['context']}\n\n"
        f"## 任务\n\n{case['task']}\n\n"
        f"## 必须保留的已知约束\n\n{preserve}\n\n"
        "直接输出正文。不要输出分析、检查表或写作说明。\n"
    )


def evaluator_packet(case: dict) -> str:
    preserve = "\n".join(f"- {item}" for item in case["must_preserve"])
    failures = "\n".join(f"- {item}" for item in case["failure_signals"])
    capabilities = "、".join(case["capabilities"])
    return f"""# 评审卡：{case['id']}

本卡包含写作者已知的完整任务语义，并额外揭示失败信号。先盲读候选正文，
再按本卡判断。每项 1-5 分，并引用候选原文。

## 写作模式

{case['mode']}

## 公开评测元数据

- 难度：{case['difficulty']}
- 能力焦点：{capabilities}

## 上下文

{case['context']}

## 任务

{case['task']}

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


def ensure_empty_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"输出目录必须为空，避免残留旧评测项: {path}")
    path.mkdir(parents=True, exist_ok=True)


def prepare(cases: list[dict], writer_output: Path, evaluator_output: Path) -> None:
    writer_output = writer_output.resolve()
    evaluator_output = evaluator_output.resolve()
    if (
        writer_output == evaluator_output
        or writer_output.is_relative_to(evaluator_output)
        or evaluator_output.is_relative_to(writer_output)
    ):
        raise ValueError("写作者包和评审者包必须使用互不包含的独立目录")
    ensure_empty_output(writer_output)
    ensure_empty_output(evaluator_output)
    for case in cases:
        (writer_output / f"{case['id']}.md").write_text(prompt_packet(case), encoding="utf-8")
        (evaluator_output / f"{case['id']}.md").write_text(evaluator_packet(case), encoding="utf-8")
    public_manifest = [
        {
            "id": case["id"],
            "mode": case["mode"],
            "difficulty": case["difficulty"],
            "capabilities": case["capabilities"],
        }
        for case in cases
    ]
    (writer_output / "manifest.json").write_text(
        json.dumps(public_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (evaluator_output / "manifest.json").write_text(
        json.dumps(public_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="准备写作 Skill 的盲评任务包")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="评测清单 JSON")
    parser.add_argument("--writer-output", help="只交给写作者的任务包目录")
    parser.add_argument("--evaluator-output", help="只交给评审者的评分卡目录")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        cases = load_cases(Path(args.manifest).expanduser().resolve())
        if bool(args.writer_output) != bool(args.evaluator_output):
            raise ValueError("生成评测包时必须同时提供 --writer-output 和 --evaluator-output")
        if args.writer_output:
            prepare(
                cases,
                Path(args.writer_output).expanduser(),
                Path(args.evaluator_output).expanduser(),
            )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    action = "已生成并分离" if args.writer_output else "校验通过"
    print(f"写作评测清单{action}：{len(cases)} 个任务，覆盖 {len({case['mode'] for case in cases})} 种模式")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
