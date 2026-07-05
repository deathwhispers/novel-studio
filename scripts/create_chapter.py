#!/usr/bin/env python3
"""新建章节快速脚本

用法:
    python3 scripts/create_chapter.py /path/to/my-novel --chapter 3
    python3 scripts/create_chapter.py /path/to/my-novel --chapter 3 --volume "第一卷-青云入门" --name "初入江湖"

自动完成:
    1. 在对应卷目录中创建章节文件
    2. 从模板复制节拍卡并填充编号
    3. 更新 90-运行/当前进度.md
    4. 更新 90-运行/连载驾驶舱.md
"""

from __future__ import annotations

import argparse
import shutil
import sys
import re
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="新建章节")
    parser.add_argument("project_dir", help="小说项目目录")
    parser.add_argument("--chapter", "-c", type=int, required=True, help="章节编号")
    parser.add_argument("--volume", "-v", default=None, help="卷目录名（如：第一卷-青云入门），默认自动选择")
    parser.add_argument("--name", "-n", default=None, help="章节名")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不执行")
    return parser.parse_args()


def find_volume_dir(project_dir: Path) -> Path | None:
    """在 30-正文/ 中查找已有的卷目录"""
    text_dir = project_dir / "30-正文"
    if not text_dir.exists():
        return None
    volumes = sorted([d for d in text_dir.iterdir() if d.is_dir() and re.search(r'第.+卷', d.name)])
    return volumes[0] if volumes else None


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser().resolve()
    ch = args.chapter

    if not project_dir.exists():
        print(f"错误：目录不存在 -> {project_dir}")
        return 1

    ch_num = f"第{ch:03d}章"
    chapter_name = f"{ch_num}-{args.name}" if args.name else ch_num

    # 确定卷目录
    if args.volume:
        volume_dir = project_dir / "30-正文" / args.volume
        if not volume_dir.exists():
            print(f"错误：卷目录不存在 -> {volume_dir}")
            return 1
    else:
        vol = find_volume_dir(project_dir)
        if vol is None:
            print("错误：未找到卷目录（30-正文/下没有 第X卷-卷名/ 目录）")
            return 1
        volume_dir = vol
        print(f"自动选择卷目录：{volume_dir.name}")

    chapter_file = volume_dir / f"{chapter_name}.md"
    beat_file = project_dir / "20-大纲" / "节拍卡" / f"{chapter_name}节拍卡.md"
    progress_file = project_dir / "90-运行" / "当前进度.md"
    cockpit_file = project_dir / "90-运行" / "连载驾驶舱.md"

    actions = []

    # 1. 创建章节文件
    if chapter_file.exists():
        actions.append(f"[跳过] 章节文件已存在：{chapter_file.name}")
    else:
        actions.append(f"[创建] 章节文件：{chapter_file.name}")
        if not args.dry_run:
            chapter_file.write_text(
                f"# {chapter_name}\n\n",
                encoding="utf-8"
            )

    # 2. 创建节拍卡（非必须，跳过时仅提示）
    if beat_file.exists():
        actions.append(f"[跳过] 节拍卡已存在：{beat_file.name}")
    elif beat_file.suffix == ".md":
        actions.append(f"[创建] 节拍卡：{beat_file.name}")
        if not args.dry_run:
            beat_file.write_text(
                f"# {chapter_name} 节拍卡\n\n"
                "## 本章任务\n\n"
                "## 核心冲突\n\n"
                "## 章尾钩子\n\n",
                encoding="utf-8"
            )

    # 3. 更新当前进度
    if progress_file.exists() and not args.dry_run:
        text = progress_file.read_text(encoding="utf-8")
        today = date.today().isoformat()
        if "- 当前章节：" in text:
            text = re.sub(r"- 当前章节：.*", f"- 当前章节：{chapter_name}", text)
            progress_file.write_text(text, encoding="utf-8")
            actions.append(f"[更新] 当前进度.md → {chapter_name}")
        else:
            actions.append(f"[提示] 当前进度.md 格式不匹配，请手动更新")

    # 4. 更新连载驾驶舱
    if cockpit_file.exists() and not args.dry_run:
        text = cockpit_file.read_text(encoding="utf-8")
        table_marker = "| Ch "
        if table_marker in text:
            lines = text.splitlines()
            actions_taken = 0
            table_count = 0
            for line in lines:
                if line.strip().startswith("| Ch"):
                    table_count += 1
            if table_count < 5:
                insert_pos = None
                for i, line in enumerate(lines):
                    if line.strip().startswith("| Ch ") and i + 1 < len(lines) and "|" in lines[i + 1]:
                        insert_pos = i + table_count
                if insert_pos:
                    text = text[:insert_pos] + f"| Ch {ch} | | | | |\n" + text[insert_pos:]
                    cockpit_file.write_text(text, encoding="utf-8")
                    actions.append(f"[更新] 连载驾驶舱.md → 添加 Ch {ch}")
            else:
                actions.append(f"[提示] 连载驾驶舱.md 已满5行，请手动管理")
        else:
            actions.append(f"[提示] 连载驾驶舱.md 格式不匹配，请手动更新")

    # 输出
    print(f"新建章节 {chapter_name} 操作清单：")
    print("-" * 40)
    for a in actions:
        print(f"  {a}")

    if args.dry_run:
        print(f"\n（--dry-run 模式，未实际执行）")
    else:
        print(f"\n✅ 完成。可开始编写 {chapter_name}。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
