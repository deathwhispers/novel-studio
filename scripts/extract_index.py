#!/usr/bin/env python3
"""前文索引自动抽取脚本

用法:
    python3 scripts/extract_index.py /path/to/novel [--update]

抽取 30-正文/章节/ 中的关键信息，写入或更新 90-运行/前文索引.md。

抽取内容:
    - 每章的 H2 标题（作为"关键名场面"）
    - 包含中文引号「」或""的句子（作为"关键对话"）
    - 角色名+动作/对话的组合
    - 关键物件名（在硬设定中登记的）

输出:
    - 默认输出到 stdout
    - --update 直接写入 90-运行/前文索引.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CHAPTER_PATTERN = re.compile(r'#\s*第\s*(\d+)\s*章')
H2_PATTERN = re.compile(r'^##\s+(.+?)$', re.MULTILINE)
QUOTE_PATTERN = re.compile(r'[「「""]([^」」""]+)[」」""]')
ITEM_PATTERN = re.compile(r'[\u4e00-\u9fff]{2,6}(剑|刀|枪|鼎|镜|珠|玉|玉佩|戒指|令牌|信物|秘籍|功法|图|谱|符|丹|瓶|碗|琴|箫|笛|杖|旗|印|玺|簪|佩|环|铃|书|卷|碎片|残魂|残片)')


def extract_chapter_number(filename: str, text: str) -> int | None:
    m = CHAPTER_PATTERN.search(text)
    if m:
        return int(m.group(1))
    m = re.search(r'chapter-(\d+)', filename)
    if m:
        return int(m.group(1))
    return None


def extract_chapter_scenes(text: str) -> list[str]:
    """提取每章的 H2 标题作为关键名场面"""
    return [m.group(1).strip() for m in H2_PATTERN.finditer(text)]


def extract_quotes(text: str, limit: int = 5) -> list[str]:
    """提取每章的关键对话"""
    quotes = QUOTE_PATTERN.findall(text)
    # 限制每章最多 5 条
    return quotes[:limit]


def extract_items(text: str) -> list[str]:
    """提取每章出现的关键物件"""
    items = set()
    for m in ITEM_PATTERN.finditer(text):
        items.add(m.group(0))
    return sorted(items)


def extract_characters_from_roles(project_dir: Path) -> list[str]:
    """从角色卡中提取已知角色名"""
    role_dir = project_dir / "10-设定" / "角色"
    if not role_dir.exists():
        return []
    names = []
    for f in role_dir.glob("*.md"):
        if f.name in ("角色卡模板.md",):
            continue
        text = f.read_text(encoding="utf-8")
        m = re.search(r'^#\s+(.+)', text, re.MULTILINE)
        if m:
            names.append(m.group(1).strip())
    return names


def extract_index(project_dir: Path, update: bool = False) -> str:
    """抽取前文索引"""
    chapter_dir = project_dir / "30-正文" / "章节"
    if not chapter_dir.exists():
        return "未找到 30-正文/章节/ 目录"

    characters = extract_characters_from_roles(project_dir)
    canon = project_dir / "10-设定" / "硬设定.md"
    canon_text = canon.read_text(encoding="utf-8") if canon.exists() else ""

    rows = []
    rows.append("| 章节 | 关键名场面 | 关键对话 | 关键物件 | 备注 |")
    rows.append("|------|----------|---------|---------|------|")

    character_first_seen = {}
    item_first_seen = {}

    for f in sorted(chapter_dir.glob("*.md")):
        if f.name in ("章节通用模板.md",):
            continue
        text = f.read_text(encoding="utf-8")
        wc = len(re.findall(r'[\u4e00-\u9fff]', text))
        if wc < 200:
            continue

        chapter_num = extract_chapter_number(f.name, text)
        chapter_label = f"第 {chapter_num} 章" if chapter_num else f.stem

        scenes = extract_chapter_scenes(text)
        scene_str = " / ".join(scenes[:3]) if scenes else "（未识别）"

        quotes = extract_quotes(text)
        quote_str = "; ".join(quotes[:3]) if quotes else "—"

        items = extract_items(text)
        # 记录首次出现
        for item in items:
            if item not in item_first_seen:
                item_first_seen[item] = chapter_label
        item_str = "、".join(items[:5]) if items else "—"

        # 记录角色首次出现
        for ch in characters:
            if ch in text and ch not in character_first_seen:
                character_first_seen[ch] = chapter_label

        rows.append(f"| {chapter_label} | {scene_str[:50]} | {quote_str[:60]} | {item_str} | [AUTO] |")

    # 角色索引
    char_rows = []
    char_rows.append("\n## 角色首次出现\n")
    char_rows.append("| 角色 | 首次出现章节 |")
    char_rows.append("|------|------------|")
    for ch, ch_label in sorted(character_first_seen.items()):
        char_rows.append(f"| {ch} | {ch_label} |")

    # 物件索引
    item_rows = []
    item_rows.append("\n## 关键物件首次出现\n")
    item_rows.append("| 物件 | 首次出现章节 |")
    item_rows.append("|------|------------|")
    for item, item_label in sorted(item_first_seen.items()):
        item_rows.append(f"| {item} | {item_label} |")

    output = "# 前文索引（自动生成）\n\n"
    output += "> 本表由 `scripts/extract_index.py` 自动生成。\n"
    output += "> 标 `[AUTO]` 的行需要人工校对。\n\n"
    output += "## 按章节索引\n\n"
    output += "\n".join(rows) + "\n"
    output += "\n".join(char_rows) + "\n"
    output += "\n".join(item_rows) + "\n"

    if update:
        index_file = project_dir / "90-运行" / "前文索引.md"
        # 如果文件已存在，保留原内容 + 追加自动生成区块
        if index_file.exists():
            existing = index_file.read_text(encoding="utf-8")
            # 找到"## 自动抽取脚本"的位置，把自动内容放在这之前
            if "## 自动抽取脚本" in existing:
                head, _, tail = existing.partition("## 自动抽取脚本")
                output = head.rstrip() + "\n\n" + output + "\n## 自动抽取脚本\n" + tail.split("## 自动抽取脚本", 1)[-1]
            else:
                output = existing + "\n\n---\n\n" + output
        index_file.write_text(output, encoding="utf-8")
        print(f"已更新: {index_file}", file=sys.stderr)

    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="从章节中自动抽取前文索引")
    parser.add_argument("project_dir", help="小说项目目录路径")
    parser.add_argument("--update", "-u", action="store_true",
                        help="直接写入 90-运行/前文索引.md")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.exists():
        print(f"错误：目录不存在 -> {project_dir}", file=sys.stderr)
        return 1

    output = extract_index(project_dir, update=args.update)
    if not args.update:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
