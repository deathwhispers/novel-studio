#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from json import loads as json_loads
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
PLUGIN_JSON = ROOT / ".codex-plugin" / "plugin.json"
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
TOKEN_RE = re.compile(r"\{\{[A-Z_]+\}\}")
VALID_TOKENS = {"{{NOVEL_TITLE}}", "{{GENRE}}", "{{PREMISE}}", "{{AUTHOR}}", "{{DATE}}", "{{PROJECT_SLUG}}"}


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
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def get_reference_paths(text: str, skill_dir: Path) -> list[Path]:
    """Extract file paths referenced in backticks from SKILL.md."""
    refs: set[Path] = set()
    for m in re.finditer(r"`([^`]+)`", text):
        path_str = m.group(1).strip()
        if path_str.startswith("http") or path_str.startswith("git") or path_str.startswith("$"):
            continue
        if not any(path_str.endswith(s) for s in (".md", ".yaml", ".json", ".py")):
            continue
        if "*" in path_str or "{" in path_str:
            continue
        clean_path = str(Path(path_str))
        p = (skill_dir / clean_path).resolve()
        if p.exists():
            refs.add(p)
            continue
        p = (ROOT / clean_path).resolve()
        if p.exists():
            refs.add(p)
    return list(refs)


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    agent_file = skill_dir / "agents" / "openai.yaml"
    ref_dir = skill_dir / "references"

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
        errors.append(f"{skill_dir.name}: frontmatter name '{name}' != directory")
    if not description or description.startswith("[TODO"):
        errors.append(f"{skill_dir.name}: description missing or TODO")

    if not agent_file.exists():
        errors.append(f"{skill_dir.name}: missing agents/openai.yaml")
    else:
        agent_text = agent_file.read_text(encoding="utf-8").strip()
        if not agent_text:
            errors.append(f"{skill_dir.name}: agents/openai.yaml is empty")

    if not ref_dir.exists():
        errors.append(f"{skill_dir.name}: missing references/ directory")

    text = skill_file.read_text(encoding="utf-8")
    for ref in get_reference_paths(text, skill_dir):
        if not ref.exists():
            errors.append(f"{skill_dir.name}: referenced file '{ref.name}' not found")

    return errors


def check_routing_coverage(errors: list[str]) -> None:
    studio_file = SKILLS_DIR / "novel-studio" / "SKILL.md"
    routing_file = SKILLS_DIR / "novel-studio" / "references" / "路由地图.md"
    skill_dirs = sorted(d.name for d in SKILLS_DIR.iterdir() if d.is_dir())

    for label, f in [("novel-studio/SKILL.md", studio_file), ("路由地图.md", routing_file)]:
        if not f.exists():
            errors.append(f"studio routing: {label} not found")
            continue
        text = f.read_text(encoding="utf-8")
        for s in skill_dirs:
            if s == "novel-studio":
                continue
            if s not in text:
                errors.append(f"studio routing: '{s}' not in {label}")


def check_plugin_listing(errors: list[str]) -> None:
    if not PLUGIN_JSON.exists():
        errors.append("plugin.json not found")
        return
    try:
        data = json_loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"plugin.json: {exc}")
        return
    skills_val = data.get("skills", "")
    if not isinstance(skills_val, str):
        errors.append(f"plugin.json: 'skills' should be a path string, got {type(skills_val).__name__}")
        return
    actual_skills = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}
    if len(actual_skills) < 12:
        errors.append(f"plugin.json: project skills/ has {len(actual_skills)} dirs, expected 12+")


def check_template_completeness(errors: list[str]) -> None:
    td = SKILLS_DIR / "novel-bootstrap" / "assets" / "novel-project-template"
    if not td.exists():
        errors.append("template directory not found")
        return
    required = [
        "00-书核/作品总表.md", "00-书核/立项单.md",
        "00-书核/长线承诺.md",
        "10-设定/硬设定.md", "10-设定/世界规则.md", "10-设定/力量体系.md",
        "10-设定/角色/主角.md", "10-设定/角色/配角.md",
        "10-设定/角色/反派.md",
        "20-大纲/全书总纲.md", "20-大纲/弧线追踪.md",
        "20-大纲/感情线追踪.md", "20-大纲/结局蓝图.md",
        "20-大纲/首卷发射台.md",
        "20-大纲/分卷/第一卷.md", "20-大纲/分卷/卷通用模板.md",
        "20-大纲/节拍卡/第一章节拍卡.md", "20-大纲/节拍卡/节拍卡通用模板.md",
        "20-大纲/因果/场景因果图.md",
        "20-大纲/回收/回收总账.md",
        "30-正文/章节/第一章.md", "30-正文/章节/章节通用模板.md",
        "30-正文/写前/章节写前检查表.md",
        "30-正文/导入/源文件索引.md",
        "40-修订/修订日志.md",
        "40-修订/修稿报告/细节修补模板.md",
        "40-修订/修稿报告/逻辑修补模板.md",
        "40-修订/修稿报告/回收修补模板.md",
        "50-归档/README.md",
        "90-运行/当前进度.md", "90-运行/连载驾驶舱.md",
        "90-运行/会话交接.md",
    ]
    for t in required:
        if not (td / t).exists():
            errors.append(f"template: missing '{t}'")


def check_template_tokens(errors: list[str]) -> None:
    td = SKILLS_DIR / "novel-bootstrap" / "assets" / "novel-project-template"
    if not td.exists():
        return
    for tf in sorted(td.rglob("*.md")):
        if "README" in tf.name:
            continue
        text = tf.read_text(encoding="utf-8")
        for m in TOKEN_RE.finditer(text):
            if m.group(0) not in VALID_TOKENS:
                errors.append(f"template: {tf.relative_to(td)} has unknown token {m.group(0)}")


def main() -> int:
    if not SKILLS_DIR.exists():
        print("skills directory not found", file=sys.stderr)
        return 1

    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
    all_errors: list[str] = []

    print(f"检查 {len(skill_dirs)} 个 skills 结构...")
    for sd in skill_dirs:
        errs = validate_skill(sd)
        status = "PASS" if not errs else "FAIL"
        all_errors.extend(errs)
        for e in errs:
            short = e.split(": ", 1)[-1] if ": " in e else e
            print(f"  [{status}] {sd.name}: {short}")
        if not errs:
            print(f"  [{status}] {sd.name}")

    print("\n检查路由覆盖...")
    routing_errs: list[str] = []
    check_routing_coverage(routing_errs)
    all_errors.extend(routing_errs)
    if routing_errs:
        for e in routing_errs:
            print(f"  [FAIL] {e}")
    else:
        print("  [PASS] 路由覆盖全部 skill")

    print("\n检查 plugin.json...")
    plugin_errs: list[str] = []
    check_plugin_listing(plugin_errs)
    all_errors.extend(plugin_errs)
    if plugin_errs:
        for e in plugin_errs:
            print(f"  [FAIL] {e}")
    else:
        print("  [PASS] plugin.json 与 skills 一致")

    print("\n检查模板文件完整性...")
    tmpl_errs: list[str] = []
    check_template_completeness(tmpl_errs)
    all_errors.extend(tmpl_errs)
    if tmpl_errs:
        for e in tmpl_errs:
            print(f"  [FAIL] {e}")
    else:
        print("  [PASS] 模板文件完整")

    print("\n检查模板 token...")
    token_errs: list[str] = []
    check_template_tokens(token_errs)
    all_errors.extend(token_errs)
    if token_errs:
        for e in token_errs:
            print(f"  [WARN] {e}")
    else:
        print("  [PASS] 模板 token 全部合法")

    if all_errors:
        print(f"\n❌ 发现问题 {len(all_errors)} 个:")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print(f"\n✅ {len(skill_dirs)} 个 skills 全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
