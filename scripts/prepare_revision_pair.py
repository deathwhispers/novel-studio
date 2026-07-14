#!/usr/bin/env python3
"""将基线与一次候选修订确定性匿名为 A/B，映射单独保存。"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from prepare_revision_evals import DEFAULT_MANIFEST, block, bullets, load_cases


def read_nonempty(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"候选文本不能为空: {path}")
    return text


def anonymize(case: dict, candidate_text: str, seed: str) -> tuple[dict[str, str], dict[str, str]]:
    baseline_text = case["original"]
    swap = hashlib.sha256(f"{seed}\0{case['id']}".encode("utf-8")).digest()[0] % 2 == 1
    if swap:
        texts = {"A": candidate_text, "B": baseline_text}
        identities = {"A": "revision", "B": "original"}
    else:
        texts = {"A": baseline_text, "B": candidate_text}
        identities = {"A": "original", "B": "revision"}
    return texts, identities


def review_packet(case: dict, texts: dict[str, str]) -> str:
    return f"""# 匿名修订对比：{case['id']}

- 写作模式：{case['mode']}
- 难度：{case['difficulty']}

## 上下文

{case['context']}

## 修订目标

{case['revision_goal']}

## 必须保留

{bullets(case['must_preserve'])}

## 失败信号

{bullets(case['failure_signals'])}

## 候选 A

{block(texts['A'])}

## 候选 B

{block(texts['B'])}

## 评审契约

1. 结论只能是“A 更有效 / B 更有效 / 持平 / 需作者判断”；相同文本允许持平。
2. 同时引用 A 与 B 的原文证据，说明修订目标是否改善。
3. 检查必须保留项，以及 voice、信息控制和节奏是否发生回退。
4. 不因长度、流畅或规整程度默认任何候选更好，不输出综合分。
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成确定性匿名的修订 A/B 评审包")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="修订案例清单 JSON")
    parser.add_argument("--case-id", required=True, help="修订案例 id")
    parser.add_argument("--revision", required=True, help="本次候选修订文本")
    parser.add_argument("--seed", required=True, help="匿名顺序种子；相同案例与种子得到相同映射")
    parser.add_argument("--review-output", required=True, help="匿名评审 Markdown 输出")
    parser.add_argument("--key-output", required=True, help="身份映射 JSON 输出；只交给操作者")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if not args.seed.strip():
            raise ValueError("--seed 不能为空")
        manifest_path = Path(args.manifest).expanduser().resolve()
        revision_path = Path(args.revision).expanduser().resolve()
        review_path = Path(args.review_output).expanduser().resolve()
        key_path = Path(args.key_output).expanduser().resolve()
        inputs = {manifest_path, revision_path}
        if review_path == key_path:
            raise ValueError("评审输出与映射输出不能使用同一路径")
        if review_path in inputs or key_path in inputs:
            raise ValueError("输出不能覆盖 manifest 或候选输入")
        if review_path.exists() or key_path.exists():
            raise ValueError("输出文件必须不存在，避免覆盖旧评审或映射")

        cases = load_cases(manifest_path)
        case = next((item for item in cases if item["id"] == args.case_id), None)
        if case is None:
            raise ValueError(f"未知案例 id: {args.case_id}")
        candidate_text = read_nonempty(revision_path)
        texts, identities = anonymize(case, candidate_text, args.seed)
        review_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(review_packet(case, texts), encoding="utf-8")
        key = {
            "case_id": case["id"],
            "seed": args.seed,
            "candidates": {
                label: {
                    "identity": identities[label],
                    "sha256": hashlib.sha256(texts[label].encode("utf-8")).hexdigest(),
                }
                for label in ("A", "B")
            },
        }
        key_path.write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    print(f"匿名评审包已生成：{review_path}\n身份映射已隔离：{key_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
