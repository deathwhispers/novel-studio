#!/usr/bin/env python3
"""从可靠原文样本与候选正文生成无评分的 voice 证据审读包。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MODES = ("商业连载", "类型长篇", "文学叙事", "短篇", "探索起草")
DEFAULT_SAMPLE_MAX_CHARS = 4000
MIN_SAMPLE_MAX_CHARS = 500
MAX_SAMPLE_MAX_CHARS = 20000


def nonempty_text(path: Path, label: str) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"{label}不是 UTF-8 文本: {path}") from error
    if not text.strip():
        raise ValueError(f"{label}不能为空: {path}")
    return text


def code_block(text: str) -> str:
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{text}\n{fence}"


def build_review(
    samples: list[tuple[Path, str]],
    candidate: tuple[Path, str],
    mode: str,
    intent: str | None,
    sample_max_chars: int,
) -> str:
    candidate_path, candidate_text = candidate
    lines = [
        "# Voice 证据审读包",
        "",
        f"- 写作模式：{mode}",
        f"- 写作意图：{intent.strip() if intent and intent.strip() else '未提供'}",
        f"- 候选来源：`{candidate_path}`（{len(candidate_text)} 字符，完整收入）",
        f"- 样本截取上限：每份 {sample_max_chars} 字符",
        "",
        "## 审读契约",
        "",
        "逐项比较注意力对象、判断方式、信息与回避策略、叙述距离、句法节奏、压力下变化。",
        "每项只归入“保持 / 合理变化 / 无依据漂移”之一；每个结论同时引用可靠样本与候选正文中的具体证据，并标明来源。",
        "写作模式和意图只用于判断变化是否有依据。不要输出综合分、相似度或自动改写稿；证据不足时说明缺口。",
        "",
        "## 可靠原文样本",
        "",
    ]
    for index, (path, text) in enumerate(samples, start=1):
        excerpt = text[:sample_max_chars]
        status = "已截断" if len(text) > len(excerpt) else "完整收入"
        lines.extend([
            f"### 样本 {index}",
            "",
            f"来源：`{path}`（原文 {len(text)} 字符，收入 {len(excerpt)} 字符，{status}）",
            "",
            code_block(excerpt),
            "",
        ])
    lines.extend([
        "## 候选正文",
        "",
        f"来源：`{candidate_path}`",
        "",
        code_block(candidate_text),
        "",
        "## 证据记录",
        "",
        "| 比较维度 | 分类 | 可靠样本证据（来源 + 引文） | 候选证据（来源 + 引文） | 判断理由 |",
        "|---|---|---|---|---|",
        "| 注意力对象 | 待审读 |  |  |  |",
        "| 判断方式 | 待审读 |  |  |  |",
        "| 信息与回避策略 | 待审读 |  |  |  |",
        "| 叙述距离 | 待审读 |  |  |  |",
        "| 句法节奏 | 待审读 |  |  |  |",
        "| 压力下变化 | 待审读 |  |  |  |",
        "",
        "## 审读结论",
        "",
        "- 保持：",
        "- 合理变化：",
        "- 无依据漂移：",
        "- 证据缺口：",
        "",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成无评分的 voice 证据审读包")
    parser.add_argument("--sample", action="append", required=True, help="可靠原文文件；重复传入，至少两份")
    parser.add_argument("--candidate", required=True, help="待审读候选正文文件")
    parser.add_argument("--mode", required=True, choices=MODES, help="当前写作模式")
    parser.add_argument("--intent", help="候选正文的预期变化或场景意图")
    parser.add_argument("--output", required=True, help="输出 Markdown 路径")
    parser.add_argument(
        "--sample-max-chars", type=int, default=DEFAULT_SAMPLE_MAX_CHARS,
        help=f"每份样本收入上限（{MIN_SAMPLE_MAX_CHARS}-{MAX_SAMPLE_MAX_CHARS}，默认 {DEFAULT_SAMPLE_MAX_CHARS}）",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if len(args.sample) < 2:
            raise ValueError("至少需要两个可靠原文样本")
        if not MIN_SAMPLE_MAX_CHARS <= args.sample_max_chars <= MAX_SAMPLE_MAX_CHARS:
            raise ValueError(
                f"--sample-max-chars 必须在 {MIN_SAMPLE_MAX_CHARS}-{MAX_SAMPLE_MAX_CHARS} 之间"
            )
        sample_paths = [Path(item).expanduser().resolve() for item in args.sample]
        if len(sample_paths) != len(set(sample_paths)):
            raise ValueError("可靠原文样本不能重复")
        candidate_path = Path(args.candidate).expanduser().resolve()
        if candidate_path in sample_paths:
            raise ValueError("候选正文不能同时作为可靠原文样本")
        output_path = Path(args.output).expanduser().resolve()
        if output_path in {*sample_paths, candidate_path}:
            raise ValueError("输出路径不能覆盖样本或候选正文")

        samples = [(path, nonempty_text(path, "可靠原文样本")) for path in sample_paths]
        candidate = (candidate_path, nonempty_text(candidate_path, "候选正文"))
        review = build_review(samples, candidate, args.mode, args.intent, args.sample_max_chars)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(review, encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    print(f"Voice 证据审读包已生成：{output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
