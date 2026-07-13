#!/usr/bin/env python3
"""扫描章节的表层文本风险，不对文学质量做综合评分。

脚本保留旧文件名以兼容现有调用。输出用于定位可能需要人工复核的片段，
不能替代叙事、人物、因果和文风审读。
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any


PROFILE_DEFAULTS: dict[str, dict[str, float | int | None]] = {
    "auto": {
        "min_chars": None,
        "max_chars": None,
        "min_dialogue_ratio": None,
        "max_dialogue_ratio": None,
        "max_avg_sentence": 40,
        "max_explain_per_1000": 7,
        "max_modifier_ratio": 0.13,
    },
    "web-serial": {
        "min_chars": 1200,
        "max_chars": 6000,
        "min_dialogue_ratio": None,
        "max_dialogue_ratio": 0.70,
        "max_avg_sentence": 38,
        "max_explain_per_1000": 7,
        "max_modifier_ratio": 0.13,
    },
    "literary": {
        "min_chars": None,
        "max_chars": None,
        "min_dialogue_ratio": None,
        "max_dialogue_ratio": None,
        "max_avg_sentence": 55,
        "max_explain_per_1000": 9,
        "max_modifier_ratio": 0.16,
    },
    "dialogue-heavy": {
        "min_chars": None,
        "max_chars": None,
        "min_dialogue_ratio": 0.20,
        "max_dialogue_ratio": 0.85,
        "max_avg_sentence": 35,
        "max_explain_per_1000": 7,
        "max_modifier_ratio": 0.13,
    },
}

EXPLAIN_PATTERNS = (
    r"[他她它](?:明白|意识到|知道|感到|注意到)",
    r"这(?:意味着|说明)",
    r"之所以.{0,30}是因为",
    r"换句话说",
    r"也就是说",
)
MODIFIER_PATTERN = re.compile(r"的|地|很|非常|特别|极其|十分")
DIALOGUE_PATTERN = re.compile(r"「[^」]*」|『[^』]*』|“[^”]*”|\"[^\"]*\"")
SENTENCE_SPLIT = re.compile(r"[。！？；.!?;]")


def count_chinese(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def body_text(text: str) -> str:
    """排除 Markdown 标题和 YAML frontmatter，减少元数据误报。"""
    if text.startswith("---\n"):
        _, separator, text = text[4:].partition("\n---\n")
        if not separator:
            text = text
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def sentence_lengths(text: str) -> list[int]:
    return [count_chinese(item) for item in SENTENCE_SPLIT.split(text) if count_chinese(item) >= 3]


def dialogue_ratio(text: str) -> float:
    total = count_chinese(text)
    if total == 0:
        return 0.0
    return sum(count_chinese(match.group(0)) for match in DIALOGUE_PATTERN.finditer(text)) / total


def line_evidence(text: str, patterns: tuple[str, ...], limit: int = 5) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    compiled = [re.compile(pattern) for pattern in patterns]
    for line_number, line in enumerate(text.splitlines(), start=1):
        matches = [match.group(0) for pattern in compiled for match in pattern.finditer(line)]
        if matches:
            evidence.append({"line": line_number, "matches": matches, "excerpt": line.strip()[:120]})
        if len(evidence) >= limit:
            break
    return evidence


def load_thresholds(profile: str, config_path: str | None) -> dict[str, float | int | None]:
    thresholds = dict(PROFILE_DEFAULTS[profile])
    if config_path:
        custom = json.loads(Path(config_path).read_text(encoding="utf-8"))
        unknown = sorted(set(custom) - set(thresholds))
        if unknown:
            raise ValueError(f"未知配置项: {', '.join(unknown)}")
        thresholds.update(custom)
    return thresholds


def scan_text(
    text: str,
    profile: str = "auto",
    thresholds: dict[str, float | int | None] | None = None,
) -> dict[str, Any]:
    clean = body_text(text)
    chars = count_chinese(clean)
    lengths = sentence_lengths(clean)
    avg_sentence = statistics.mean(lengths) if lengths else 0.0
    sentence_stddev = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
    dialogue = dialogue_ratio(clean)
    explain_count = sum(len(re.findall(pattern, clean)) for pattern in EXPLAIN_PATTERNS)
    explain_per_1000 = explain_count / chars * 1000 if chars else 0.0
    modifier_ratio = len(MODIFIER_PATTERN.findall(clean)) / chars if chars else 0.0
    limits = dict(thresholds or PROFILE_DEFAULTS[profile])
    risks: list[dict[str, Any]] = []

    def add(code: str, message: str, evidence: list[dict[str, Any]] | None = None) -> None:
        risks.append({"code": code, "message": message, "evidence": evidence or []})

    minimum = limits.get("min_chars")
    maximum = limits.get("max_chars")
    if minimum is not None and chars < float(minimum):
        add("length_below_profile", f"正文 {chars} 字，低于 {profile} 档位参考下限 {minimum}；请结合章节功能复核。")
    if maximum is not None and chars > float(maximum):
        add("length_above_profile", f"正文 {chars} 字，高于 {profile} 档位参考上限 {maximum}；请结合章节功能复核。")

    min_dialogue = limits.get("min_dialogue_ratio")
    max_dialogue = limits.get("max_dialogue_ratio")
    if min_dialogue is not None and dialogue < float(min_dialogue):
        add("dialogue_below_profile", f"对话占比 {dialogue:.1%}，低于所选档位参考值；低对话本身不是质量问题。")
    if max_dialogue is not None and dialogue > float(max_dialogue):
        add("dialogue_above_profile", f"对话占比 {dialogue:.1%}，建议复核动作、空间和潜台词是否不足。")

    max_avg = limits.get("max_avg_sentence")
    if max_avg is not None and avg_sentence > float(max_avg):
        add("long_sentence_cluster", f"平均句长 {avg_sentence:.1f} 字，建议抽查长句是否存在指代或层级负担。")

    max_explain = limits.get("max_explain_per_1000")
    if max_explain is not None and explain_count >= 4 and explain_per_1000 > float(max_explain):
        add(
            "explain_density",
            f"解释性句式约 {explain_per_1000:.1f} 次/千字；逐处判断是否真的替代了行动或潜台词。",
            line_evidence(text, EXPLAIN_PATTERNS),
        )

    max_modifier = limits.get("max_modifier_ratio")
    if max_modifier is not None and chars >= 80 and modifier_ratio > float(max_modifier):
        add("modifier_density", f"常见修饰标记占比 {modifier_ratio:.1%}；仅作为抽查信号，不建议机械删词。")

    return {
        "profile": profile,
        "metrics": {
            "chinese_chars": chars,
            "sentence_count": len(lengths),
            "avg_sentence_length": round(avg_sentence, 2),
            "sentence_length_stddev": round(sentence_stddev, 2),
            "dialogue_ratio": round(dialogue, 4),
            "explain_patterns": explain_count,
            "explain_per_1000": round(explain_per_1000, 2),
            "modifier_ratio": round(modifier_ratio, 4),
        },
        "risks": risks,
        "disclaimer": "这些是表层风险信号，不是文学质量分数；必须结合章节功能、题材、人物和上下文人工复核。",
    }


def find_chapter(project: Path, chapter: str) -> Path | None:
    text_dir = project / "30-正文"
    matches = sorted(text_dir.rglob(f"{chapter}.md"))
    if not matches:
        matches = sorted(text_dir.rglob(f"*{chapter}*.md"))
    return matches[0] if matches else None


def render_human(report: dict[str, Any], chapter: str, chapter_file: Path, verbose: bool) -> str:
    metrics = report["metrics"]
    lines = [
        "=" * 48,
        f"章节文本风险扫描：{chapter}",
        "=" * 48,
        f"文件：{chapter_file}",
        f"档位：{report['profile']}",
        f"中文字数：{metrics['chinese_chars']:,}",
        f"平均句长：{metrics['avg_sentence_length']:.1f} 字",
        f"句长离散度：{metrics['sentence_length_stddev']:.1f}",
        f"对话占比：{metrics['dialogue_ratio']:.1%}",
        "",
        report["disclaimer"],
    ]
    risks = report["risks"]
    if not risks:
        lines.extend(["", "未发现达到当前阈值的表层风险；这不代表章节已经通过叙事质量审计。"])
    else:
        lines.extend(["", f"发现 {len(risks)} 类待人工复核信号："])
        for risk in risks:
            lines.append(f"- [{risk['code']}] {risk['message']}")
            if verbose:
                for item in risk["evidence"]:
                    lines.append(f"  L{item['line']}: {item['excerpt']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="扫描章节表层文本风险（不做文学质量评分）")
    parser.add_argument("project_dir", help="小说项目目录")
    parser.add_argument("--chapter", "-c", required=True, help="章节名，如 第001章")
    parser.add_argument("--profile", choices=sorted(PROFILE_DEFAULTS), default="auto", help="可选题材/发布档位")
    parser.add_argument("--config", help="JSON 阈值覆盖文件")
    parser.add_argument("--json", action="store_true", help="输出结构化 JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示命中片段")
    parser.add_argument("--fail-on-risk", action="store_true", help="发现风险时返回退出码 2")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    chapter_file = find_chapter(project, args.chapter)
    if chapter_file is None:
        print(f"错误：未找到章节文件 -> 30-正文/.../{args.chapter}*", file=sys.stderr)
        return 1
    try:
        thresholds = load_thresholds(args.profile, args.config)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"错误：无法读取扫描配置：{error}", file=sys.stderr)
        return 1
    report = scan_text(chapter_file.read_text(encoding="utf-8"), args.profile, thresholds)
    report["chapter"] = args.chapter
    report["file"] = str(chapter_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_human(report, args.chapter, chapter_file, args.verbose))
    return 2 if args.fail_on_risk and report["risks"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
