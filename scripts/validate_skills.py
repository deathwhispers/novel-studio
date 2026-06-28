#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")


def parse_frontmatter(skill_file: Path) -> dict[str, str]:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening frontmatter delimiter")

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        raise ValueError("missing closing frontmatter delimiter")

    data: dict[str, str] = {}
    for line in lines[1:end_index]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    agent_file = skill_dir / "agents" / "openai.yaml"

    if not skill_file.exists():
        return [f"{skill_dir.name}: missing SKILL.md"]

    try:
        frontmatter = parse_frontmatter(skill_file)
    except ValueError as exc:
        return [f"{skill_dir.name}: {exc}"]

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    if not NAME_RE.match(name):
        errors.append(f"{skill_dir.name}: invalid skill name '{name}'")
    if name != skill_dir.name:
        errors.append(f"{skill_dir.name}: frontmatter name does not match directory")
    if not description or description.startswith("[TODO"):
        errors.append(f"{skill_dir.name}: description is missing or still TODO")
    if not agent_file.exists():
        errors.append(f"{skill_dir.name}: missing agents/openai.yaml")

    return errors


def main() -> int:
    if not SKILLS_DIR.exists():
        print("skills directory not found", file=sys.stderr)
        return 1

    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    all_errors: list[str] = []

    for skill_dir in skill_dirs:
        all_errors.extend(validate_skill(skill_dir))

    if all_errors:
        print("skill validation failed:")
        for error in all_errors:
            print(f"- {error}")
        return 1

    print(f"validated {len(skill_dirs)} skills successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
