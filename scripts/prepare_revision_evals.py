#!/usr/bin/env python3
"""校验并生成隔离的修订任务与评审 rubric。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "skills" / "novel-writing" / "assets" / "evals" / "revision-cases.json"
MODES = {"商业连载", "类型长篇", "文学叙事", "短篇", "探索起草"}
DIFFICULTIES = {"standard", "adversarial"}
FIELDS = {
    "id", "mode", "difficulty", "context", "original", "revision_goal",
    "must_preserve", "failure_signals",
}


def nonempty_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label}必须是非空数组")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{label}必须只包含非空字符串")
    return value


def load_cases(path: Path) -> list[dict]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or not cases:
        raise ValueError("修订评测清单必须是非空数组")
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or set(case) != FIELDS:
            raise ValueError(f"修订案例字段必须严格为: {sorted(FIELDS)}")
        case_id = case["id"]
        if not isinstance(case_id, str) or not re.fullmatch(r"[a-z0-9-]+", case_id):
            raise ValueError(f"非法案例 id: {case_id}")
        if case_id in seen:
            raise ValueError(f"重复案例 id: {case_id}")
        if case["mode"] not in MODES:
            raise ValueError(f"未知写作模式: {case['mode']}")
        if case["difficulty"] not in DIFFICULTIES:
            raise ValueError(f"未知评测难度: {case_id}: {case['difficulty']}")
        for field in ("context", "original", "revision_goal"):
            if not isinstance(case[field], str) or not case[field].strip():
                raise ValueError(f"{field} 必须是非空字符串: {case_id}")
        nonempty_list(case["must_preserve"], f"{case_id} must_preserve")
        nonempty_list(case["failure_signals"], f"{case_id} failure_signals")
        seen.add(case_id)
    return cases


def block(text: str) -> str:
    longest = max((len(item) for item in re.findall(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def writer_packet(case: dict) -> str:
    return f"""# 修订任务：{case['id']}

- 写作模式：{case['mode']}
- 难度：{case['difficulty']}

## 上下文

{case['context']}

## 待修文本

{block(case['original'])}

## 修订目标

{case['revision_goal']}

## 必须保留

{bullets(case['must_preserve'])}

直接输出修订后的完整正文。不要输出分析、评分或修改说明。
"""


def evaluator_packet(case: dict) -> str:
    return f"""# 修订评审 rubric：{case['id']}

修订是待验证假设，不预先宣称新版本更好。比较时允许旧版本更有效或两者持平。

- 写作模式：{case['mode']}
- 难度：{case['difficulty']}

## 上下文

{case['context']}

## 基线文本

{block(case['original'])}

## 修订目标

{case['revision_goal']}

## 必须保留

{bullets(case['must_preserve'])}

## 失败信号

{bullets(case['failure_signals'])}

## 评审要求

- 检查目标问题是否改善，并同时检查必须保留项、voice、信息控制与节奏是否回退。
- 结论引用两个版本的原文证据；不要因为文本更长、更顺或更规整就判定更好。
- 不输出综合分；给出“新版本更有效 / 基线更有效 / 持平 / 需作者判断”及理由。
"""


def ensure_empty(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"输出目录必须为空，避免残留旧案例: {path}")
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
    ensure_empty(writer_output)
    ensure_empty(evaluator_output)
    public_manifest = [
        {"id": case["id"], "mode": case["mode"], "difficulty": case["difficulty"]}
        for case in cases
    ]
    for case in cases:
        (writer_output / f"{case['id']}.md").write_text(writer_packet(case), encoding="utf-8")
        (evaluator_output / f"{case['id']}.md").write_text(evaluator_packet(case), encoding="utf-8")
    manifest_text = json.dumps(public_manifest, ensure_ascii=False, indent=2) + "\n"
    (writer_output / "manifest.json").write_text(manifest_text, encoding="utf-8")
    (evaluator_output / "manifest.json").write_text(manifest_text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="准备修订能力盲评任务包")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="修订案例清单 JSON")
    parser.add_argument("--writer-output", help="只交给修订者的任务目录")
    parser.add_argument("--evaluator-output", help="只交给评审者的 rubric 目录")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        cases = load_cases(Path(args.manifest).expanduser().resolve())
        if bool(args.writer_output) != bool(args.evaluator_output):
            raise ValueError("生成评测包时必须同时提供 --writer-output 和 --evaluator-output")
        if args.writer_output:
            prepare(cases, Path(args.writer_output).expanduser(), Path(args.evaluator_output).expanduser())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    action = "已生成并分离" if args.writer_output else "校验通过"
    print(f"修订评测清单{action}：{len(cases)} 个案例")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
