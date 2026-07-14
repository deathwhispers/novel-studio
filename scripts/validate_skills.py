#!/usr/bin/env python3
"""Validate the current eight-skill novel-skills distribution."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
BACKTICK_RE = re.compile(r"`([^`]+)`")
RESOURCE_SUFFIXES = (".md", ".yaml", ".yml", ".json", ".py")


def parse_frontmatter(skill_file: Path) -> dict[str, str]:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening frontmatter delimiter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("missing closing frontmatter delimiter") from exc

    data: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def resolve_resource(path_str: str, skill_dir: Path) -> Path | None:
    """Resolve bundled resource references while ignoring novel workspace outputs."""
    path_str = path_str.strip()
    if not path_str.endswith(RESOURCE_SUFFIXES) or any(c in path_str for c in "*{}<>"):
        return None
    if path_str.startswith(("http://", "https://", "$")):
        return None
    if path_str.startswith(("references/", "assets/", "scripts/", "agents/", "../")):
        return (skill_dir / path_str).resolve()
    if path_str.startswith("novel-"):
        return (SKILLS_DIR / path_str).resolve()
    return None


def validate_openai_yaml(agent_file: Path, skill_name: str) -> list[str]:
    errors: list[str] = []
    if not agent_file.exists():
        return ["missing agents/openai.yaml"]
    text = agent_file.read_text(encoding="utf-8")
    for key in ("display_name:", "short_description:", "default_prompt:"):
        if key not in text:
            errors.append(f"agents/openai.yaml missing {key[:-1]}")
    if f"${skill_name}" not in text:
        errors.append(f"agents/openai.yaml default_prompt must mention ${skill_name}")
    short_match = re.search(r'^\s*short_description:\s*"([^"]+)"\s*$', text, re.MULTILINE)
    if short_match and not 25 <= len(short_match.group(1)) <= 64:
        errors.append("agents/openai.yaml short_description must be 25-64 characters")
    return errors


def validate_skill(skill_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return ["missing SKILL.md"], warnings

    try:
        frontmatter = parse_frontmatter(skill_file)
    except ValueError as exc:
        return [str(exc)], warnings

    if set(frontmatter) != {"name", "description"}:
        errors.append("frontmatter must contain only name and description")
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if not NAME_RE.fullmatch(name):
        errors.append(f"invalid skill name '{name}'")
    if name != skill_dir.name:
        errors.append(f"frontmatter name '{name}' != directory")
    if len(description) < 20:
        errors.append("description is too short to provide reliable triggers")

    errors.extend(validate_openai_yaml(skill_dir / "agents" / "openai.yaml", name))

    text = skill_file.read_text(encoding="utf-8")
    if len(text.splitlines()) > 500:
        errors.append("SKILL.md exceeds 500 lines")
    for path_str in BACKTICK_RE.findall(text):
        resource = resolve_resource(path_str, skill_dir)
        if resource is not None and not resource.exists():
            errors.append(f"referenced resource not found: {path_str}")

    for ref in sorted((skill_dir / "references").rglob("*.md")) if (skill_dir / "references").exists() else []:
        lines = ref.read_text(encoding="utf-8").splitlines()
        if len(lines) > 100 and not any("目录" in line or "Contents" in line for line in lines[:40]):
            warnings.append(f"long reference has no opening TOC: {ref.relative_to(skill_dir)} ({len(lines)} lines)")
    return errors, warnings


def check_routing(errors: list[str]) -> None:
    skill_names = sorted(d.name for d in SKILLS_DIR.iterdir() if d.is_dir())
    files = [
        SKILLS_DIR / "novel-studio" / "SKILL.md",
        SKILLS_DIR / "novel-studio" / "references" / "路由地图.md",
        SKILLS_DIR / "novel-studio" / "references" / "技能调用速查.md",
    ]
    for file in files:
        if not file.exists():
            errors.append(f"routing file not found: {file.relative_to(ROOT)}")
            continue
        text = file.read_text(encoding="utf-8")
        for name in skill_names:
            if name != "novel-studio" and name not in text:
                errors.append(f"{file.relative_to(ROOT)} does not route {name}")


def check_template(errors: list[str]) -> None:
    template = SKILLS_DIR / "novel-project" / "assets" / "novel-project-template"
    init_script = SKILLS_DIR / "novel-project" / "scripts" / "init_novel_project.py"
    if not init_script.exists():
        errors.append("novel-project initialization script not found")
    required = [
        "00-书核/作品总表.md",
        "00-书核/立项单.md",
        "10-设定/硬设定.md",
        "10-设定/文风指南.md",
        "20-大纲/全书总纲.md",
        "20-大纲/分卷/volume-01.md",
        "20-大纲/节拍卡/节拍卡通用模板.md",
        "30-正文/第一卷-初入江湖/第001章.md",
        "40-修订/体检报告/说明.md",
        "50-归档/说明.md",
        "90-运行/当前进度.md",
        "90-运行/决策记录.md",
        "90-运行/项目配置.md",
    ]
    for rel in required:
        if not (template / rel).exists():
            errors.append(f"template file not found: {rel}")


def check_writing_contract(errors: list[str]) -> None:
    """Prevent universal entry points from reintroducing retired one-mode rules."""
    files = [
        ROOT / "README.md",
        ROOT / "QUICKSTART.md",
        ROOT / "DEPLOYMENT.md",
        SKILLS_DIR / "novel-studio" / "SKILL.md",
        SKILLS_DIR / "novel-project" / "SKILL.md",
        SKILLS_DIR / "novel-outline" / "SKILL.md",
        SKILLS_DIR / "novel-writing" / "SKILL.md",
        SKILLS_DIR / "novel-quality" / "SKILL.md",
    ]
    banned = (
        "默认每章 2000-2500",
        "强制执行完整的章节写作流程",
        "每章至少要明确 10 项",
        "每章的章尾必须有",
        "一章只能一个 POV",
    )
    for file in files:
        text = file.read_text(encoding="utf-8")
        for phrase in banned:
            if phrase in text:
                errors.append(
                    f"universal writing contract contains retired rule: "
                    f"{file.relative_to(ROOT)} -> {phrase}"
                )

    for relative in (
        "scripts/build_context_pack.py",
        "scripts/evaluate_chapter.py",
        "scripts/prepare_writing_evals.py",
    ):
        if not os.access(ROOT / relative, os.X_OK):
            errors.append(f"script is not executable: {relative}")


def check_duplicate_references(warnings: list[str]) -> None:
    seen: dict[bytes, Path] = {}
    for file in sorted(SKILLS_DIR.glob("*/references/**/*.md")):
        content = file.read_bytes()
        if content in seen:
            warnings.append(
                f"duplicate reference: {file.relative_to(ROOT)} == {seen[content].relative_to(ROOT)}"
            )
        else:
            seen[content] = file


def main() -> int:
    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
    errors: list[str] = []
    warnings: list[str] = []
    print(f"检查 {len(skill_dirs)} 个 skills...")
    for skill_dir in skill_dirs:
        skill_errors, skill_warnings = validate_skill(skill_dir)
        errors.extend(f"{skill_dir.name}: {item}" for item in skill_errors)
        warnings.extend(f"{skill_dir.name}: {item}" for item in skill_warnings)
        print(f"  [{'PASS' if not skill_errors else 'FAIL'}] {skill_dir.name}")

    check_routing(errors)
    check_template(errors)
    check_writing_contract(errors)
    check_duplicate_references(warnings)

    if warnings:
        print(f"\n⚠️  {len(warnings)} 个建议：")
        for warning in warnings:
            print(f"  - {warning}")
    if errors:
        print(f"\n❌ {len(errors)} 个错误：")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"\n✅ {len(skill_dirs)} 个 skills 结构与资源链接全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
