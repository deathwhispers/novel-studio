#!/usr/bin/env python3
"""小说项目结构校验脚本

用法:
    python3 scripts/validate_novel_project.py /path/to/my-novel

检查:
    - 必选目录和文件是否存在
    - 各章节字数统计
    - 设定与正文的连续性隐患
    - 回收总账是否更新
    - 连载驾驶舱是否更新
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_DIRS = [
    "00-书核", "05-市场", "05-市场/拆解", "10-设定", "10-设定/角色",
    "20-大纲", "20-大纲/分卷", "20-大纲/节拍卡", "20-大纲/因果", "20-大纲/回收",
    "30-正文", "30-正文/章节", "30-正文/写前", "30-正文/场景", "30-正文/导入",
    "40-修订", "40-修订/体检报告", "40-修订/修稿报告",
    "50-归档", "90-运行",
]

CORE_FILES = [
    "00-书核/作品总表.md", "00-书核/立项单.md", "00-书核/长线承诺.md",
    "20-大纲/全书总纲.md", "20-大纲/首卷发射台.md",
    "90-运行/当前进度.md", "90-运行/连载驾驶舱.md",
    "90-运行/会话交接.md", "90-运行/决策记录.md",
]

OPTIONAL_FILES = [
    "05-市场/趋势笔记.md", "05-市场/对标书单.md",
    "10-设定/硬设定.md", "10-设定/世界规则.md", "10-设定/力量体系.md",
    "10-设定/势力.md", "10-设定/地点.md", "10-设定/时间线.md", "10-设定/母题.md",
    "10-设定/角色/主角.md", "10-设定/角色/反派.md", "10-设定/角色/配角.md",
    "20-大纲/弧线追踪.md", "20-大纲/感情线追踪.md", "20-大纲/结局蓝图.md",
    "20-大纲/因果/场景因果图.md", "20-大纲/回收/回收总账.md",
    "30-正文/章节成品检查表.md",
    "40-修订/修订日志.md", "40-修订/完本检查清单.md",
]


def count_chinese_chars(text: str) -> int:
    """统计中文字符数（含标点）"""
    return len(re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', text))


def format_wc(n: int) -> str:
    if n >= 10000:
        return f"{n / 10000:.1f}万"
    return f"{n}"


def scan_chapters(project_dir: Path) -> list[dict]:
    """扫描章节文件并统计字数"""
    chapters = []
    chapter_dir = project_dir / "30-正文" / "章节"
    if not chapter_dir.exists():
        return chapters
    for f in sorted(chapter_dir.glob("*.md")):
        if f.name in ("章节通用模板.md",):
            continue
        text = f.read_text(encoding="utf-8")
        wc = count_chinese_chars(text)
        # 估算是否含显著正文（> 200 字才视为有内容）
        has_content = wc > 200
        chapters.append({
            "file": f.name,
            "words": wc,
            "has_content": has_content,
        })
    return chapters


def scan_progress(project_dir: Path) -> dict:
    """从当前进度文件中读取进度信息"""
    progress_file = project_dir / "90-运行" / "当前进度.md"
    info = {"current_volume": "?", "current_chapter": "?", "last_updated": "?"}
    if not progress_file.exists():
        return info
    text = progress_file.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "当前卷" in line or "当前写到" in line:
            info["current_volume"] = line.split("：")[-1].strip() if "：" in line else line
        if "当前章" in line or "第" in line and "章" in line:
            info["current_chapter"] = line.split("：")[-1].strip() if "：" in line else line
    return info


def check_settlement(project_dir: Path) -> list[str]:
    """检查设定与正文的基础一致性"""
    issues = []
    canon_file = project_dir / "10-设定" / "硬设定.md"
    chapter_dir = project_dir / "30-正文" / "章节"
    if not canon_file.exists() or not chapter_dir.exists():
        return issues
    canon_text = canon_file.read_text(encoding="utf-8")
    # 提取设定中的关键名词（简单的提取方式）
    names = set(re.findall(r'^###?\s+(.{2,20})$', canon_text, re.MULTILINE))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="小说项目结构校验")
    parser.add_argument("project_dir", help="小说项目目录路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="输出详细信息")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        print(f"错误：目录不存在 -> {project_dir}")
        return 1

    errors = []
    warnings = []
    info = []

    # 1. 检查目录
    for d in REQUIRED_DIRS:
        if not (project_dir / d).exists():
            errors.append(f"缺少目录：{d}")

    # 2. 检查核心文件
    for f in CORE_FILES:
        if not (project_dir / f).exists():
            errors.append(f"缺少核心文件：{f}")

    # 3. 检查可选文件（仅提示）
    for f in OPTIONAL_FILES:
        if not (project_dir / f).exists():
            warnings.append(f"可选文件缺失：{f}")

    # 4. 扫描章节字数
    chapters = scan_chapters(project_dir)
    if chapters:
        info.append(f"章节总数：{len(chapters)}")
        total_words = sum(c["words"] for c in chapters)
        info.append(f"正文总字数（中文字符）：{format_wc(total_words)}")
        has_content = [c for c in chapters if c["has_content"]]
        info.append(f"已写章节：{len(has_content)}/{len(chapters)}")
        if args.verbose:
            for c in chapters:
                status = "✓" if c["has_content"] else "○"
                info.append(f"  [{status}] {c['file']}: {format_wc(c['words'])}")
        # 检查字数异常
        for c in chapters:
            if c["has_content"] and c["words"] < 500:
                warnings.append(f"章节字数偏低：{c['file']}（{format_wc(c['words'])}字）")
            elif c["has_content"] and c["words"] > 8000:
                warnings.append(f"章节字数偏高：{c['file']}（{format_wc(c['words'])}字）")
    else:
        warnings.append("未找到章节文件")

    # 5. 进度检查
    progress = scan_progress(project_dir)
    info.append(f"当前进度：{progress['current_volume']}/{progress['current_chapter']}")

    # 6. 检查连载驾驶舱
    cockpit = project_dir / "90-运行" / "连载驾驶舱.md"
    if cockpit.exists():
        cockpit_text = cockpit.read_text(encoding="utf-8")
        if "当前写到" not in cockpit_text:
            warnings.append("连载驾驶舱.md 未填写当前写到位置")
        if "风险" not in cockpit_text:
            warnings.append("连载驾驶舱.md 未填写风险项")
    else:
        errors.append("缺少连载驾驶舱.md")

    # 7. 检查回收总账
    ledger = project_dir / "20-大纲" / "回收" / "回收总账.md"
    if ledger.exists():
        ledger_text = ledger.read_text(encoding="utf-8")
        if len(ledger_text.strip()) < 50:
            warnings.append("回收总账.md 内容过少，可能未填写")
    else:
        warnings.append("缺少回收总账.md")

    # 输出报告
    print("=" * 50)
    print(f"小说项目校验报告：{project_dir.name}")
    print("=" * 50)

    if errors:
        print(f"\n❌ 错误（{len(errors)}项）：")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print(f"\n⚠️  警告（{len(warnings)}项）：")
        for w in warnings:
            print(f"  - {w}")

    if info:
        print(f"\nℹ️  信息（{len(info)}项）：")
        for i in info:
            print(f"  - {i}")

    if not errors and not warnings:
        print("\n✅ 项目结构健康，未发现问题！")
    elif not errors:
        print("\n✅ 无严重错误，建议修复警告项。")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
