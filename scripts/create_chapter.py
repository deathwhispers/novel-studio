#!/usr/bin/env python3
"""新建章节快速脚本

用法:
    python3 scripts/create_chapter.py /path/to/my-novel --chapter 3

自动完成:
    1. 从模板复制章节文件并填充编号
    2. 从模板复制节拍卡并填充编号
    3. 更新 90-运行/当前进度.md
    4. 更新 90-运行/连载驾驶舱.md
    5. 复制写前检查表
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import date
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="新建章节")
    parser.add_argument("project_dir", help="小说项目目录")
    parser.add_argument("--chapter", "-c", type=int, required=True, help="章节编号")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不执行")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser().resolve()
    ch = args.chapter

    if not project_dir.exists():
        print(f"错误：目录不存在 -> {project_dir}")
        return 1

    ch_num = f"第{to_chinese(ch)}章" if ch <= 20 else f"第{ch}章"
    chapter_file = project_dir / "30-正文" / "章节" / f"{ch_num}.md"
    beat_file = project_dir / "20-大纲" / "节拍卡" / f"{ch_num}节拍卡.md"
    checklist_file = project_dir / "30-正文" / "写前" / f"{ch_num}写前检查表.md"
    progress_file = project_dir / "90-运行" / "当前进度.md"
    cockpit_file = project_dir / "90-运行" / "连载驾驶舱.md"

    template_chapter = project_dir / "30-正文" / "章节" / "章节通用模板.md"
    template_beat = project_dir / "20-大纲" / "节拍卡" / "节拍卡通用模板.md"
    template_checklist = project_dir / "30-正文" / "写前" / "章节写前检查表.md"

    actions = []

    # 1. 创建章节文件
    if chapter_file.exists():
        actions.append(f"[跳过] 章节文件已存在：{chapter_file.name}")
    elif template_chapter.exists():
        actions.append(f"[创建] 章节文件：{chapter_file.name}")
        if not args.dry_run:
            shutil.copy2(template_chapter, chapter_file)
            text = chapter_file.read_text(encoding="utf-8")
            text = text.replace("{{章节号}}", ch_num).replace("{{日期}}", date.today().isoformat())
            chapter_file.write_text(text, encoding="utf-8")
    else:
        actions.append(f"[警告] 章节通用模板不存在，跳过")

    # 2. 创建节拍卡
    if beat_file.exists():
        actions.append(f"[跳过] 节拍卡已存在：{beat_file.name}")
    elif template_beat.exists():
        actions.append(f"[创建] 节拍卡：{beat_file.name}")
        if not args.dry_run:
            shutil.copy2(template_beat, beat_file)
            text = beat_file.read_text(encoding="utf-8")
            text = text.replace("{{章节号}}", ch_num)
            beat_file.write_text(text, encoding="utf-8")
    else:
        actions.append(f"[警告] 节拍卡通用模板不存在，跳过")

    # 3. 创建写前检查表
    if checklist_file.exists():
        actions.append(f"[跳过] 检查表已存在：{checklist_file.name}")
    elif template_checklist.exists():
        actions.append(f"[创建] 写前检查表：{checklist_file.name}")
        if not args.dry_run:
            shutil.copy2(template_checklist, checklist_file)
            text = checklist_file.read_text(encoding="utf-8")
            text = text.replace("{{章节号}}", ch_num)
            checklist_file.write_text(text, encoding="utf-8")
    else:
        actions.append(f"[提示] 写前检查表模板不存在，跳过")

    # 4. 更新当前进度
    if progress_file.exists() and not args.dry_run:
        text = progress_file.read_text(encoding="utf-8")
        today = date.today().isoformat()
        if "- 当前章节：" in text:
            text = text.replace("- 当前章节：", f"- 当前章节：{ch_num}")
            progress_file.write_text(text, encoding="utf-8")
            actions.append(f"[更新] 当前进度.md → {ch_num}")
        else:
            actions.append(f"[提示] 当前进度.md 格式不匹配，请手动更新")

    # 5. 更新连载驾驶舱
    if cockpit_file.exists() and not args.dry_run:
        text = cockpit_file.read_text(encoding="utf-8")
        # 尝试在近5章任务表添加一行
        table_marker = "| Ch "
        if table_marker in text:
            # 找到最后一个表行并替换
            lines = text.splitlines()
            new_lines = []
            table_count = 0
            for line in lines:
                if line.strip().startswith("| Ch"):
                    table_count += 1
                new_lines.append(line)
            # 如果表格行少于5行，追加一行
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
            actions.append(f"[提示] 连载驾驶舱.md 格式不匹配，请手动更新")

    # 输出
    print(f"新建章节 {ch_num} 操作清单：")
    print("-" * 40)
    for a in actions:
        print(f"  {a}")

    if args.dry_run:
        print(f"\n（--dry-run 模式，未实际执行）")
    else:
        print(f"\n✅ 完成。可开始编写 {ch_num}。")

    return 0


def to_chinese(n: int) -> str:
    mapping = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
                "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十"]
    return mapping[n] if 0 < n <= 20 else str(n)


if __name__ == "__main__":
    raise SystemExit(main())
