#!/usr/bin/env python3
"""为指定章节组装可审计的最小上下文包。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CHAPTER_RE = re.compile(r"第(\d+)章")


def chapter_number(value: str) -> int:
    match = re.search(r"\d+", value)
    if not match:
        raise ValueError(f"无法识别章节号: {value}")
    return int(match.group(0))


def first_existing(project: Path, candidates: list[str]) -> Path | None:
    for relative in candidates:
        path = project / relative
        if path.is_file():
            return path
    return None


def find_chapter_files(project: Path) -> list[tuple[int, Path]]:
    found: list[tuple[int, Path]] = []
    for path in (project / "30-正文").rglob("*.md"):
        match = CHAPTER_RE.search(path.stem)
        if match:
            found.append((int(match.group(1)), path))
    return sorted(found, key=lambda item: (item[0], str(item[1])))


def document_keys(path: Path) -> set[str]:
    keys = {path.stem}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return keys
    heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if heading:
        keys.add(heading.group(1).strip())
    return {key for key in keys if len(key) >= 2 and "模板" not in key and "说明" not in key}


def find_relevant_docs(project: Path, beat_text: str) -> list[tuple[str, Path, str]]:
    relevant: list[tuple[str, Path, str]] = []
    groups = (
        ("相关人物", project / "10-设定" / "角色"),
        ("相关地点", project / "10-设定" / "地点"),
    )
    for label, directory in groups:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            if any(key in beat_text for key in document_keys(path)):
                relevant.append((label, path, "compact"))
    return relevant


def trim_text(text: str, limit: int, tail: bool = False) -> str:
    if len(text) <= limit:
        return text.strip()
    if tail:
        return "[…前文已截断…]\n" + text[-limit:].lstrip()
    return text[:limit].rstrip() + "\n[…后文已截断…]"


def collect_sources(project: Path, number: int, includes: list[str]) -> list[tuple[str, Path, str]]:
    sources: list[tuple[str, Path, str]] = []

    def add(label: str, path: Path | None, mode: str = "head") -> None:
        if path and path.is_file() and all(existing[1] != path for existing in sources):
            sources.append((label, path, mode))

    beat = first_existing(project, [
        f"20-大纲/节拍卡/chapter-{number:03d}.md",
        f"20-大纲/节拍卡/chapter-{number}.md",
    ])
    add("本章节拍卡", beat)

    chapter_files = find_chapter_files(project)
    previous = [item for item in chapter_files if item[0] < number]
    anchor = next((path for chapter, path in chapter_files if chapter == number), None)
    if anchor is None and previous:
        anchor = previous[-1][1]
    volume_files = sorted((project / "20-大纲" / "分卷").glob("*.md"))
    selected_volume = volume_files[0] if volume_files else None
    if anchor and volume_files:
        volume_dirs = sorted({path.parent for _, path in chapter_files}, key=str)
        if anchor.parent in volume_dirs:
            index = volume_dirs.index(anchor.parent) + 1
            selected_volume = first_existing(project, [
                f"20-大纲/分卷/volume-{index:02d}.md",
                f"20-大纲/分卷/volume-{index}.md",
            ]) or selected_volume
    if previous:
        add("最近正文末段", previous[-1][1], "tail")

    for relative in includes:
        path = (project / relative).resolve()
        try:
            path.relative_to(project)
        except ValueError as error:
            raise ValueError(f"附加文件必须位于项目内: {relative}") from error
        if not path.is_file():
            raise ValueError(f"附加文件不存在: {relative}")
        add(f"附加：{relative}", path, "compact")

    beat_text = beat.read_text(encoding="utf-8") if beat else ""
    for label, path, mode in find_relevant_docs(project, beat_text):
        add(label, path, mode)

    add("文风指南", first_existing(project, ["10-设定/文风指南.md"]))
    add("硬设定", first_existing(project, ["10-设定/硬设定.md", "10-设定/世界规则.md"]), "compact")
    add("场景因果", first_existing(project, ["20-大纲/因果/场景因果图.md"]), "compact")
    add("回收总账", first_existing(project, ["20-大纲/回收/回收总账.md"]), "compact")
    add("当前进度", first_existing(project, ["90-运行/当前进度.md"]), "compact")
    add("分卷计划", selected_volume, "summary")
    add("作品总表", first_existing(project, ["00-书核/作品总表.md"]), "summary")
    return sources


def build_context_pack(
    project: Path,
    number: int,
    includes: list[str] | None = None,
    max_chars: int = 18000,
    per_file_chars: int = 3500,
    previous_chars: int = 3000,
) -> str:
    sources = collect_sources(project, number, includes or [])
    sections: list[str] = [
        f"# 第{number:03d}章最小上下文包",
        "",
        "> 自动汇总只负责召回，不替代作者判断。缺失文件会跳过；写前只确认当前模式真正需要的信息。",
        "",
        "## 来源清单",
        "",
    ]
    for label, path, _ in sources:
        sections.append(f"- {label}: `{path.relative_to(project)}`")

    used = len("\n".join(sections))
    for label, path, mode in sources:
        if mode == "tail":
            allowance = previous_chars
        elif mode == "compact":
            allowance = min(1800, per_file_chars)
        elif mode == "summary":
            allowance = min(1600, per_file_chars)
        else:
            allowance = per_file_chars
        allowance = min(allowance, max_chars - used)
        if allowance < 200:
            sections.extend(["", "## 截断提示", "", "上下文包达到总字符上限；其余来源只保留在来源清单中。"])
            break
        content = trim_text(path.read_text(encoding="utf-8"), allowance, tail=mode == "tail")
        section = f"\n## {label}\n\n<!-- source: {path.relative_to(project)} -->\n\n{content}"
        sections.append(section)
        used += len(section)

    sections.extend([
        "",
        "## 写前最后确认",
        "",
        "- 当前写作模式、单位和这次最想完成或发现的是什么？",
        "- 当前视角注意什么；人物想靠近、逃避、理解或维持什么？",
        "- 压力、关系、信息或形式将怎样运动；若不变化，停顿有什么意义？",
        "- 哪些 hard canon 不能破坏，哪些未知项可以通过正文探索？",
        "- 需要延续的 voice 证据来自哪段可靠文本？",
    ])
    return "\n".join(sections).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="组装章节最小上下文包")
    parser.add_argument("project_dir", help="小说项目目录")
    parser.add_argument("--chapter", "-c", required=True, help="目标章节号，如 12 或 第012章")
    parser.add_argument("--include", action="append", default=[], help="额外加入的项目内相对路径，可重复")
    parser.add_argument("--output", "-o", help="输出文件；省略时打印到 stdout")
    parser.add_argument("--max-chars", type=int, default=18000, help="上下文包字符上限")
    parser.add_argument("--per-file-chars", type=int, default=3500, help="普通来源单文件字符上限")
    parser.add_argument("--previous-chars", type=int, default=3000, help="最近正文保留的末尾字符数")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    if not project.is_dir():
        print(f"错误：项目目录不存在: {project}", file=sys.stderr)
        return 1
    try:
        number = chapter_number(args.chapter)
        pack = build_context_pack(
            project,
            number,
            args.include,
            args.max_chars,
            args.per_file_chars,
            args.previous_chars,
        )
    except (OSError, ValueError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    if args.output:
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(pack, encoding="utf-8")
        print(f"上下文包已生成: {output}")
    else:
        print(pack, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
