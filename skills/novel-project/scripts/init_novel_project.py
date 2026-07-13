#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import date
from pathlib import Path


TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml"}
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "novel-project-template"

MINIMAL_FILES = {
    "00-书核/作品总表.md",
    "00-书核/立项单.md",
    "00-书核/长线承诺.md",
    "10-设定/世界规则.md",
    "10-设定/硬设定.md",
    "10-设定/文风指南.md",
    "10-设定/角色/主角.md",
    "20-大纲/全书总纲.md",
    "20-大纲/分卷/volume-01.md",
    "20-大纲/节拍卡/chapter-001.md",
    "20-大纲/因果/场景因果图.md",
    "20-大纲/回收/回收总账.md",
    "30-正文/章节/章节通用模板.md",
    "90-运行/当前进度.md",
    "90-运行/会话交接.md",
    "90-运行/决策记录.md",
    "90-运行/章节增量/说明.md",
    "90-运行/写作训练日志.md",
}

REQUIRED_PROJECT_DIRS = (
    "00-书核", "05-市场", "05-市场/拆解", "10-设定", "10-设定/角色",
    "20-大纲", "20-大纲/分卷", "20-大纲/节拍卡", "20-大纲/因果", "20-大纲/回收",
    "30-正文", "40-修订", "40-修订/体检报告", "40-修订/修稿报告", "50-归档", "90-运行",
)

LONGFORM_ONLY_PREFIXES = (
    "10-设定/势力/",
    "10-设定/反派/",
)
LONGFORM_ONLY_FILES = {
    "20-大纲/多主角分工表.md",
    "20-大纲/多线并行管理表.md",
    "20-大纲/前30章留存期管理.md",
    "20-大纲/升级阶段.md",
    "90-运行/人物状态变迁日志.md",
    "90-运行/全角色卷末快照.md",
    "90-运行/角色立场漂移记录.md",
    "90-运行/连续性查询.md",
}


def slugify(value: str) -> str:
    slug = []
    last_dash = False
    for char in value.strip().lower():
        if char.isalnum():
            slug.append(char)
            last_dash = False
        elif not last_dash:
            slug.append("-")
            last_dash = True
    return "".join(slug).strip("-") or "novel-project"


def replace_tokens(path: Path, tokens: dict[str, str]) -> None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return
    text = path.read_text(encoding="utf-8")
    for key, value in tokens.items():
        text = text.replace(key, value)
    path.write_text(text, encoding="utf-8")


def include_in_profile(relative: Path, profile: str) -> bool:
    name = relative.as_posix()
    if profile == "minimal":
        return name in MINIMAL_FILES
    if profile == "serial":
        return name not in LONGFORM_ONLY_FILES and not name.startswith(LONGFORM_ONLY_PREFIXES)
    return True


def copy_template(output_dir: Path, tokens: dict[str, str], profile: str) -> int:
    copied = 0
    for source in TEMPLATE_DIR.rglob("*"):
        relative = source.relative_to(TEMPLATE_DIR)
        target = output_dir / relative
        if source.is_dir():
            continue
        if not include_in_profile(relative, profile):
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        replace_tokens(target, tokens)
        copied += 1
    for relative in REQUIRED_PROJECT_DIRS:
        (output_dir / relative).mkdir(parents=True, exist_ok=True)
    return copied


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a novel project workspace")
    parser.add_argument("--output", required=True, help="Target directory for the project")
    parser.add_argument("--title", required=True, help="Novel title")
    parser.add_argument("--genre", required=True, help="Primary genre")
    parser.add_argument("--premise", required=True, help="One-line story premise")
    parser.add_argument("--author", default="Unknown", help="Author or pen name")
    parser.add_argument(
        "--profile",
        choices=("minimal", "serial", "longform"),
        default="serial",
        help="Template depth: minimal, serial (default), or longform",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output).expanduser().resolve()

    if not TEMPLATE_DIR.exists():
        print(f"template directory not found: {TEMPLATE_DIR}", file=sys.stderr)
        return 1

    if output_dir.exists() and any(output_dir.iterdir()):
        print(f"refusing to initialize into non-empty directory: {output_dir}", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    tokens = {
        "{{书名}}": args.title,
        "{{题材}}": args.genre,
        "{{前提}}": args.premise,
        "{{作者}}": args.author,
        "{{日期}}": date.today().isoformat(),
        "{{项目标识}}": slugify(args.title),
    }
    copied = copy_template(output_dir, tokens, args.profile)
    print(f"initialized {args.profile} novel project at {output_dir} ({copied} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
