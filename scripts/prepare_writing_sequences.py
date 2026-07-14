#!/usr/bin/env python3
"""校验并生成多轮写作压力包，隔离写作者与评审者信息。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "skills" / "novel-writing" / "assets" / "evals" / "writing-sequences.json"
MODES = {"商业连载", "类型长篇", "文学叙事", "短篇", "探索起草"}
SEQUENCE_FIELDS = {"id", "mode", "initial_context", "invariants", "capabilities", "turns"}
TURN_FIELDS = {"id", "task", "must_preserve", "failure_signals"}
TURN_OPTIONAL_FIELDS = {"recall_from"}


def string_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label}必须是非空数组")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{label}必须只包含非空字符串")
    if len(value) != len(set(value)):
        raise ValueError(f"{label}不能包含重复项")
    return value


def load_sequences(path: Path) -> list[dict]:
    sequences = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(sequences, list) or not sequences:
        raise ValueError("序列清单必须是非空数组")
    sequence_ids: set[str] = set()
    for sequence in sequences:
        if not isinstance(sequence, dict) or set(sequence) != SEQUENCE_FIELDS:
            raise ValueError(f"序列字段必须严格为: {sorted(SEQUENCE_FIELDS)}")
        sequence_id = sequence["id"]
        if not isinstance(sequence_id, str) or not re.fullmatch(r"[a-z0-9-]+", sequence_id):
            raise ValueError(f"非法序列 id: {sequence_id}")
        if sequence_id in sequence_ids:
            raise ValueError(f"重复序列 id: {sequence_id}")
        if sequence["mode"] not in MODES:
            raise ValueError(f"未知写作模式: {sequence['mode']}")
        if not isinstance(sequence["initial_context"], str) or not sequence["initial_context"].strip():
            raise ValueError(f"初始上下文不能为空: {sequence_id}")
        string_list(sequence["invariants"], f"{sequence_id} invariants")
        string_list(sequence["capabilities"], f"{sequence_id} capabilities")
        turns = sequence["turns"]
        if not isinstance(turns, list) or len(turns) < 4:
            raise ValueError(f"每条序列至少需要 4 轮: {sequence_id}")
        turn_ids: list[str] = []
        for turn in turns:
            if not isinstance(turn, dict):
                raise ValueError(f"轮次必须是对象: {sequence_id}")
            fields = set(turn)
            if not TURN_FIELDS <= fields or fields - TURN_FIELDS - TURN_OPTIONAL_FIELDS:
                raise ValueError(f"轮次字段非法: {sequence_id}: {sorted(fields)}")
            turn_id = turn["id"]
            if not isinstance(turn_id, str) or not re.fullmatch(r"[a-z0-9-]+", turn_id):
                raise ValueError(f"非法轮次 id: {sequence_id}: {turn_id}")
            if turn_id in turn_ids:
                raise ValueError(f"重复轮次 id: {sequence_id}: {turn_id}")
            if not isinstance(turn["task"], str) or not turn["task"].strip():
                raise ValueError(f"轮次任务不能为空: {sequence_id}: {turn_id}")
            string_list(turn["must_preserve"], f"{sequence_id}/{turn_id} must_preserve")
            string_list(turn["failure_signals"], f"{sequence_id}/{turn_id} failure_signals")
            references = turn.get("recall_from", [])
            if references:
                string_list(references, f"{sequence_id}/{turn_id} recall_from")
            elif not isinstance(references, list):
                raise ValueError(f"recall_from 必须是数组: {sequence_id}: {turn_id}")
            invalid = [reference for reference in references if reference not in turn_ids]
            if invalid:
                raise ValueError(f"非法或非前序轮次引用: {sequence_id}/{turn_id}: {invalid}")
            turn_ids.append(turn_id)
        if turn_ids[0] not in turns[-1].get("recall_from", []):
            raise ValueError(f"末轮必须显式召回首轮: {sequence_id}: {turn_ids[0]}")
        sequence_ids.add(sequence_id)
    return sequences


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def writer_packet(sequence: dict, turn_index: int) -> str:
    turn = sequence["turns"][turn_index]
    prior_ids = [item["id"] for item in sequence["turns"][:turn_index]]
    recall = turn.get("recall_from", [])
    prior_label = "、".join(prior_ids) if prior_ids else "无（首轮）"
    recall_label = "、".join(recall) if recall else "无显式远距召回目标"
    slots = (
        "本轮为首轮，无此前候选输出。"
        if not prior_ids
        else "先按顺序读取或粘贴此前所有候选输出与状态增量，再开始本轮。\n\n"
             "### 此前候选输出\n\n[在此粘贴或读取此前各轮候选]\n\n"
             "### 此前状态增量\n\n[在此粘贴或读取此前各轮状态增量]"
    )
    return f"""# 多轮写作任务：{sequence['id']} / {turn['id']}

- 写作模式：{sequence['mode']}
- 能力焦点：{'、'.join(sequence['capabilities'])}
- 此前轮次：{prior_label}
- 本轮显式召回：{recall_label}

## 初始上下文

{sequence['initial_context']}

## 全序列不变量

{bullets(sequence['invariants'])}

## 运行前输入

{slots}

## 本轮任务

{turn['task']}

## 本轮必须保留

{bullets(turn['must_preserve'])}

直接输出本轮正文，并在末尾附短小“状态增量”：只记录正文真实产生的变化、仍未知信息与下一轮需继承项。
"""


def evaluator_packet(sequence: dict) -> str:
    sections = []
    for index, turn in enumerate(sequence["turns"], start=1):
        recall = "、".join(turn.get("recall_from", [])) or "无"
        sections.append(f"""### 第 {index} 轮：{turn['id']}

- 显式召回：{recall}

任务：{turn['task']}

必须保留：
{bullets(turn['must_preserve'])}

失败信号：
{bullets(turn['failure_signals'])}
""")
    return f"""# 多轮写作评审卡：{sequence['id']}

- 写作模式：{sequence['mode']}
- 能力焦点：{'、'.join(sequence['capabilities'])}

## 初始上下文

{sequence['initial_context']}

## 全序列不变量

{bullets(sequence['invariants'])}

## 轮次公开语义与隐藏失败信号

{''.join(sections)}
## 评审要求

1. 按轮次顺序读取全部候选正文与状态增量，不孤立评分单轮。
2. 检查状态继承、远距离回声、模式稳定、voice 与未授权 canon；每个结论引用至少两个轮次的候选证据并标明轮次。
3. 区分“保持”“合理变化”“无依据漂移”以及“证据不足”。
4. 不输出综合分。给出最影响序列稳定性的证据、可保留之处和最小复核建议。
"""


def ensure_empty_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"输出目录必须为空，避免残留旧序列: {path}")
    path.mkdir(parents=True, exist_ok=True)


def prepare(sequences: list[dict], writer_output: Path, evaluator_output: Path) -> None:
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
    public_manifest = []
    for sequence in sequences:
        sequence_dir = writer_output / sequence["id"]
        sequence_dir.mkdir()
        for index, turn in enumerate(sequence["turns"]):
            (sequence_dir / f"{turn['id']}.md").write_text(
                writer_packet(sequence, index), encoding="utf-8"
            )
        (evaluator_output / f"{sequence['id']}.md").write_text(
            evaluator_packet(sequence), encoding="utf-8"
        )
        public_manifest.append({
            "id": sequence["id"],
            "mode": sequence["mode"],
            "capabilities": sequence["capabilities"],
            "turns": [turn["id"] for turn in sequence["turns"]],
        })
    manifest_text = json.dumps(public_manifest, ensure_ascii=False, indent=2) + "\n"
    (writer_output / "manifest.json").write_text(manifest_text, encoding="utf-8")
    (evaluator_output / "manifest.json").write_text(manifest_text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="准备多轮写作连续性压力包")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="序列清单 JSON")
    parser.add_argument("--writer-output", help="只交给写作者的逐轮任务目录")
    parser.add_argument("--evaluator-output", help="只交给评审者的序列评审目录")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        sequences = load_sequences(Path(args.manifest).expanduser().resolve())
        if bool(args.writer_output) != bool(args.evaluator_output):
            raise ValueError("生成压力包时必须同时提供 --writer-output 和 --evaluator-output")
        if args.writer_output:
            prepare(sequences, Path(args.writer_output).expanduser(), Path(args.evaluator_output).expanduser())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    action = "已生成并分离" if args.writer_output else "校验通过"
    print(f"多轮写作序列{action}：{len(sequences)} 条，{sum(len(item['turns']) for item in sequences)} 轮")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
