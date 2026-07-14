#!/usr/bin/env python3
"""为指定章节组装可审计的最小上下文包。"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CHAPTER_RE = re.compile(r"第(\d+)章")
PLACEHOLDER_RE = re.compile(r"未起草|【在此处写章节正文】|\{\{.*?\}\}")
GENERIC_ENTITY_STEMS = {
    "主角", "配角", "反派", "角色卡模板", "角色模板",
    "地点模板", "物件模板", "地点", "物件",
}
CORE_LABELS = {"项目配置", "作品承诺", "硬设定", "当前进度"}


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


def markdown_section(text: str, heading: str) -> str | None:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        return None
    rest = text[match.end():]
    end = re.search(r"^##\s+", rest, re.MULTILINE)
    return rest[:end.start() if end else None].strip()


def chapter_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    body = markdown_section(text, "正文")
    if body is None:
        body = "\n".join(
            line for line in text.splitlines()
            if not line.startswith("#") and not line.startswith("当前状态：")
        ).strip()
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()
    return "" if PLACEHOLDER_RE.fullmatch(body) else body


def has_substantive_body(path: Path) -> bool:
    body = chapter_body(path)
    return len(re.findall(r"[\u4e00-\u9fffA-Za-z0-9]", body)) >= 3


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


def has_substantive_entity_content(path: Path) -> bool:
    """过滤初始化后的通用卡和未填卡。

    具名实体卡只要有有效正文即可；“主角.md”这类通用文件则必须出现
    已填的姓名/名称字段，避免“主角”一词召回整张空模板。
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    if path.stem in GENERIC_ENTITY_STEMS:
        filled_identity = re.search(
            r"(?:\*\*)?(?:姓名|名称)(?:\*\*)?[ \t]*[：:][ \t]*([^\s>|{【][^\n]*)",
            text,
        )
        return bool(filled_identity)
    cleaned = re.sub(r"<!--.*?-->|\{\{.*?\}\}", "", text, flags=re.DOTALL)
    meaningful = [
        line.strip() for line in cleaned.splitlines()
        if line.strip()
        and not line.lstrip().startswith(("#", ">", "|", "- **"))
        and "例如" not in line
        and not re.fullmatch(r"[-:|空\s]+", line)
    ]
    return len("".join(meaningful)) >= 3


def find_relevant_docs(project: Path, source_text: str) -> list[tuple[str, Path, str]]:
    relevant: list[tuple[str, Path, str]] = []
    groups = (
        ("相关人物", project / "10-设定" / "角色"),
        ("相关地点", project / "10-设定" / "地点"),
        ("相关物件", project / "10-设定" / "物件"),
    )
    for label, directory in groups:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            if has_substantive_entity_content(path) and any(
                key in source_text for key in document_keys(path)
            ):
                relevant.append((label, path, "compact"))
    return relevant


def trim_text(text: str, limit: int, tail: bool = False) -> str:
    if limit <= 0:
        return ""
    clean = text.strip()
    if len(clean) <= limit:
        return clean
    marker = "[…前文已截断…]\n" if tail else "\n[…后文已截断…]"
    if limit <= len(marker):
        return marker.strip()[:limit]
    if tail:
        payload = clean[-(limit - len(marker)):].lstrip()
        return marker + payload
    payload = clean[:limit - len(marker)].rstrip()
    return payload + marker


def recent_deltas(project: Path, number: int, limit: int = 5) -> list[Path]:
    directory = project / "90-运行" / "章节增量"
    if not directory.is_dir():
        return []
    found: list[tuple[int, Path]] = []
    for path in directory.glob("chapter-*.md"):
        match = re.search(r"chapter-(\d+)", path.stem)
        if match and int(match.group(1)) < number:
            found.append((int(match.group(1)), path))
    return [path for _, path in sorted(found)[-limit:]]


def collect_sources(
    project: Path,
    number: int,
    includes: list[str],
    task: str = "",
) -> list[tuple[str, Path, str]]:
    sources: list[tuple[str, Path, str]] = []

    def add(label: str, path: Path | None, mode: str = "head") -> None:
        if path and path.is_file() and all(existing[1] != path for existing in sources):
            sources.append((label, path, mode))

    # 这四类来源定义“这是什么项目、承诺什么、不能破坏什么、
    # 已经写到哪里”，紧预算下也先于长节拍卡和正文。
    add("项目配置", first_existing(project, ["90-运行/项目配置.md"]), "compact")
    add("作品承诺", first_existing(project, ["00-书核/作品总表.md", "00-书核/立项单.md"]), "summary")
    add("硬设定", first_existing(project, ["10-设定/硬设定.md", "10-设定/世界规则.md"]), "compact")
    add("当前进度", first_existing(project, ["90-运行/当前进度.md"]), "compact")

    beat = first_existing(project, [
        f"20-大纲/节拍卡/chapter-{number:03d}.md",
        f"20-大纲/节拍卡/chapter-{number}.md",
    ])
    add("本章节拍卡", beat)

    chapter_files = find_chapter_files(project)
    written_chapters = [item for item in chapter_files if has_substantive_body(item[1])]
    previous = [item for item in written_chapters if item[0] < number]
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
        add("最近有效正文末段", previous[-1][1], "body-tail")

    deltas = recent_deltas(project, number)
    for path in deltas:
        delta_number = re.search(r"(\d+)", path.stem)
        label = f"最近状态增量 Ch {int(delta_number.group(1))}" if delta_number else "最近状态增量"
        add(label, path, "compact")

    for relative in includes:
        path = (project / relative).resolve()
        try:
            path.relative_to(project)
        except ValueError as error:
            raise ValueError(f"附加文件必须位于项目内: {relative}") from error
        if not path.is_file():
            raise ValueError(f"附加文件不存在: {relative}")
        add(f"附加：{relative}", path, "compact")

    retrieval_text = "\n".join([
        task,
        beat.read_text(encoding="utf-8") if beat else "",
        chapter_body(previous[-1][1]) if previous else "",
        *(path.read_text(encoding="utf-8") for path in deltas),
    ])
    for label, path, mode in find_relevant_docs(project, retrieval_text):
        add(label, path, mode)

    add("文风指南", first_existing(project, ["10-设定/文风指南.md"]))
    add("场景因果", first_existing(project, ["20-大纲/因果/场景因果图.md"]), "compact")
    add("回收总账", first_existing(project, ["20-大纲/回收/回收总账.md"]), "compact")
    add("分卷计划", selected_volume, "summary")
    return sources


def build_context_pack(
    project: Path,
    number: int,
    includes: list[str] | None = None,
    task: str = "",
    max_chars: int = 18000,
    per_file_chars: int = 3500,
    previous_chars: int = 3000,
) -> str:
    if max_chars < 800:
        raise ValueError("max_chars 不能小于 800")
    if per_file_chars < 200 or previous_chars < 200:
        raise ValueError("单文件字符预算不能小于 200")
    sources = collect_sources(project, number, includes or [], task)
    intro = (
        f"# 第{number:03d}章最小上下文包\n\n"
        "> 自动召回不替代作者判断；项目承诺、模式、hard canon 和进度优先。\n"
    )
    footer = (
        "\n## 写前最后确认\n\n"
        "- 这次要完成或发现什么？\n"
        "- 哪些 hard canon 不能破坏，需延续哪段 voice 证据？\n"
    )
    # 为来源状态预留空间。清单过长时聚合“因预算省略”项，但不伪装成全部已纳入。
    metadata_budget = min(1200, max(180, max_chars // 5))
    content_budget = max_chars - len(intro) - len(footer) - metadata_budget - 2
    content_sections: list[str] = []
    included: list[tuple[str, Path]] = []
    omitted: list[tuple[str, Path]] = []

    def raw_for(path: Path, mode: str) -> str:
        return chapter_body(path) if mode == "body-tail" else path.read_text(encoding="utf-8")

    remaining = content_budget
    for index, (label, path, mode) in enumerate(sources):
        if mode == "body-tail":
            allowance = previous_chars
        elif mode == "compact":
            allowance = min(1800, per_file_chars)
        elif mode == "summary":
            allowance = min(1600, per_file_chars)
        else:
            allowance = per_file_chars
        relative = path.relative_to(project)
        section_head = f"\n## {label}\n<!-- source: {relative} -->\n"
        later_core = sum(
            1 for later_label, _, _ in sources[index + 1:]
            if later_label in CORE_LABELS
        )
        # 给后续核心来源保留“标题 + 最小内容”的位置。
        reserve = later_core * 80
        available = remaining - len(section_head) - reserve
        minimum = 24 if label in CORE_LABELS else 120
        if available < minimum:
            omitted.append((label, path))
            continue
        allowance = min(allowance, available)
        content = trim_text(raw_for(path, mode), allowance, tail=mode == "body-tail")
        section = section_head + content + "\n"
        if len(section) > remaining:
            omitted.append((label, path))
            continue
        content_sections.append(section)
        included.append((label, path))
        remaining -= len(section)

    status_lines = ["## 来源清单"]
    used = len(status_lines[0]) + 1
    for label, path in included:
        line = f"- [纳入] {label}: `{path.relative_to(project)}`"
        if used + len(line) + 1 > metadata_budget:
            break
        status_lines.append(line)
        used += len(line) + 1
    omitted_shown = 0
    for label, path in omitted:
        line = f"- [因预算省略] {label}: `{path.relative_to(project)}`"
        if used + len(line) + 1 > metadata_budget - 24:
            break
        status_lines.append(line)
        used += len(line) + 1
        omitted_shown += 1
    if len(omitted) > omitted_shown:
        line = f"- [因预算省略] 另 {len(omitted) - omitted_shown} 项"
        if used + len(line) + 1 <= metadata_budget:
            status_lines.append(line)
    status = "\n".join(status_lines) + "\n"
    result = intro + "\n" + status + "".join(content_sections) + footer
    # 计算已包含截断标记、来源清单和所有连接换行；此断言是硬边界的回归保护。
    if len(result) > max_chars:
        raise AssertionError(f"上下文包超出硬上限: {len(result)} > {max_chars}")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="组装章节最小上下文包")
    parser.add_argument("project_dir", help="小说项目目录")
    parser.add_argument("--chapter", "-c", required=True, help="目标章节号，如 12 或 第012章")
    parser.add_argument("--include", action="append", default=[], help="额外加入的项目内相对路径，可重复")
    parser.add_argument("--task", default="", help="当前写作任务，用于召回相关人物、地点和物件")
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
            args.task,
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
