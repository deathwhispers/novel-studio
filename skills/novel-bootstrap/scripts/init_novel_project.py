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


def copy_template(output_dir: Path, tokens: dict[str, str]) -> None:
    for source in TEMPLATE_DIR.rglob("*"):
        relative = source.relative_to(TEMPLATE_DIR)
        target = output_dir / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        replace_tokens(target, tokens)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a novel project workspace")
    parser.add_argument("--output", required=True, help="Target directory for the project")
    parser.add_argument("--title", required=True, help="Novel title")
    parser.add_argument("--genre", required=True, help="Primary genre")
    parser.add_argument("--premise", required=True, help="One-line story premise")
    parser.add_argument("--author", default="Unknown", help="Author or pen name")
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
        "{{NOVEL_TITLE}}": args.title,
        "{{GENRE}}": args.genre,
        "{{PREMISE}}": args.premise,
        "{{AUTHOR}}": args.author,
        "{{DATE}}": date.today().isoformat(),
        "{{PROJECT_SLUG}}": slugify(args.title),
    }
    copy_template(output_dir, tokens)
    print(f"initialized novel project at {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
