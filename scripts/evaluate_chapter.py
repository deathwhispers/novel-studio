#!/usr/bin/env python3
"""章节质量评估脚本

对章节做基础质量评分，扫描字数、句长、对话密度、AI解释腔、形容词密度。

用法:
    python3 scripts/evaluate_chapter.py /path/to/my-novel --chapter 第一章
    python3 scripts/evaluate_chapter.py /path/to/my-novel --chapter 第二章 --verbose
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def count_chinese(text: str) -> int:
    return len(re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', text))


def count_sentences(text: str) -> int:
    return len(re.findall(r'[。！？；.!?;]', text))


def avg_sentence_length(text: str) -> float:
    sentences = re.split(r'[。！？；.!?;]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    if not sentences:
        return 0
    return sum(count_chinese(s) for s in sentences) / len(sentences)


def count_dialogue_blocks(text: str) -> int:
    return len(re.findall(r'「[^」]*」|"[^"]*"|『[^』]*』', text))


def count_explain_patterns(text: str) -> int:
    patterns = [
        r'他明白', r'她意识到', r'他知道', r'她感到',
        r'因为', r'意味着', r'说明', r'似乎',
        r'仿佛', r'显得', r'注意到',
    ]
    return sum(len(re.findall(p, text)) for p in patterns)


def count_adj_density(text: str) -> float:
    chinese_chars = count_chinese(text)
    if chinese_chars == 0:
        return 0
    matches = len(re.findall(r'的|地|很|非常|特别|极其|十分', text))
    return matches / chinese_chars


def dialogue_ratio(text: str) -> float:
    total = count_chinese(text)
    if total == 0:
        return 0
    dia_blocks = re.findall(r'「[^」]+」', text)
    dia_chars = sum(count_chinese(b) for b in dia_blocks)
    return dia_chars / total


def main() -> int:
    parser = argparse.ArgumentParser(description="章节质量评估")
    parser.add_argument("project_dir", help="小说项目目录")
    parser.add_argument("--chapter", "-c", required=True, help="章节名，如 第一章")
    parser.add_argument("--verbose", "-v", action="store_true", help="输出详细信息")
    args = parser.parse_args()

    project = Path(args.project_dir).expanduser().resolve()
    text_dir = project / "30-正文"
    # 在所有卷目录中搜索匹配的章节文件
    chapter_files = sorted(text_dir.rglob(f"{args.chapter}.md"))
    if not chapter_files:
        # 也支持全局通配搜索
        chapter_files = sorted(text_dir.rglob(f"*{args.chapter}*.md"))
    if not chapter_files:
        print(f"错误：未找到章节文件 -> 30-正文/.../{args.chapter}*", file=sys.stderr)
        return 1
    chapter_file = chapter_files[0]

    text = chapter_file.read_text(encoding="utf-8")
    wc = count_chinese(text)
    sentences = count_sentences(text)
    avg_len = avg_sentence_length(text)
    dia_blocks = count_dialogue_blocks(text)
    dia_ratio_val = dialogue_ratio(text)
    explain_val = count_explain_patterns(text)
    adj_val = count_adj_density(text)

    scores = {}
    issues = []

    if wc < 500:
        scores["字数"] = 2
        issues.append("字数偏低（<500字），章节太短")
    elif wc < 1500:
        scores["字数"] = 6
        issues.append("字数偏少（<1500字），考虑扩充")
    elif wc < 3000:
        scores["字数"] = 9
    elif wc < 5000:
        scores["字数"] = 8
    else:
        scores["字数"] = 6
        issues.append("字数偏高（>5000字），注意段落节奏")

    if avg_len < 15:
        scores["句长"] = 9
    elif avg_len < 25:
        scores["句长"] = 8
    elif avg_len < 35:
        scores["句长"] = 6
    else:
        scores["句长"] = 3
        issues.append("句长偏高（均>35字），检查是否多长句堆砌")

    if dia_ratio_val < 0.1:
        scores["对话"] = 4
        issues.append("对话占比偏少（<10%），考虑增加对话推进")
    elif dia_ratio_val < 0.2:
        scores["对话"] = 7
    elif dia_ratio_val < 0.5:
        scores["对话"] = 9
    else:
        scores["对话"] = 7

    if explain_val > 10:
        scores["解释腔"] = 3
        issues.append("解释腔模式过多（>10处），建议用动作替代心理描述")
    elif explain_val > 5:
        scores["解释腔"] = 6
        issues.append("存在解释腔模式（>5处），中等风险")
    else:
        scores["解释腔"] = 9

    if adj_val > 0.15:
        scores["形容词"] = 4
        issues.append("形容词/副词密度偏高，建议用具体动作替代")
    elif adj_val > 0.10:
        scores["形容词"] = 7
    else:
        scores["形容词"] = 9

    total = sum(scores.values())
    max_score = len(scores) * 10
    pct = total / max_score * 100

    print(f"{'='*45}")
    print(f"章节质量评估：{args.chapter}")
    print(f"{'='*45}")
    print(f"  中文字数：{wc:,}")
    print(f"  句子数：{sentences}")
    print(f"  平均句长：{avg_len:.1f} 字")
    print(f"  对话块数：{dia_blocks}")
    print(f"  对话占比：{dia_ratio_val:.1%}")

    print(f"\n评分明细：")
    for k, v in sorted(scores.items()):
        bar = "█" * (v // 2) + "░" * ((10 - v) // 2)
        print(f"  {k}：{v}/10 {bar}")

    grade_map = {"A": 85, "B": 70, "C": 55}
    grade = "A"
    for g, threshold in sorted(grade_map.items(), key=lambda x: -x[1]):
        if pct >= threshold:
            grade = g
            break
    else:
        grade = "D"

    print(f"\n综合评分：{pct:.0f}/100  等级：{grade}")

    if issues:
        print(f"\n发现 {len(issues)} 个问题：")
        for issue in issues:
            print(f"  - {issue}")

    if args.verbose:
        print(f"\n详细数据：")
        print(f"  解释腔匹配数：{explain_val}")
        print(f"  形容词密度：{adj_val:.3f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
