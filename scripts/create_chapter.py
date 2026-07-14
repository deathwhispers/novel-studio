#!/usr/bin/env python3
"""新建章节快速脚本

用法:
    python3 scripts/create_chapter.py /path/to/my-novel --chapter 3
    python3 scripts/create_chapter.py /path/to/my-novel --chapter 3 --volume "第一卷-青云入门" --name "初入江湖"

自动完成:
    1. 在对应卷目录中创建章节文件
    2. 创建可裁剪的写作支点
    3. 更新 90-运行/当前进度.md
    4. 若项目启用了连载驾驶舱，则同步更新
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


VALID_PROFILES = {"minimal", "serial", "longform"}
VALID_MODES = {"商业连载", "类型长篇", "文学叙事", "短篇", "探索起草"}


def read_writing_mode(project_dir: Path) -> str | None:
    """只从完整、有效的新版项目配置继承模式。

    旧项目或非法配置仍可建章，但不猜测其模式。
    """
    config = project_dir / "90-运行" / "项目配置.md"
    if not config.is_file():
        return None
    text = config.read_text(encoding="utf-8")
    values: dict[str, str] = {}
    for key in ("模板档位", "写作模式", "配置版本", "连载工具"):
        match = re.search(rf"^- {key}：\s*(\S+)\s*$", text, re.MULTILINE)
        if match:
            values[key] = match.group(1)
    if (
        values.get("模板档位") not in VALID_PROFILES
        or values.get("写作模式") not in VALID_MODES
        or values.get("配置版本") != "1"
        or values.get("连载工具") not in {"启用", "停用"}
    ):
        return None
    return values["写作模式"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="新建章节")
    parser.add_argument("project_dir", help="小说项目目录")
    parser.add_argument("--chapter", "-c", type=int, required=True, help="章节编号")
    parser.add_argument("--volume", "-v", default=None, help="卷目录名（如：第一卷-青云入门），默认自动选择")
    parser.add_argument("--name", "-n", default=None, help="章节名")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不执行")
    return parser.parse_args()


def find_volume_dir(project_dir: Path) -> Path | None:
    """优先选择卷目录；minimal 项目回退到通用章节目录。"""
    text_dir = project_dir / "30-正文"
    if not text_dir.exists():
        return None
    volumes = sorted([d for d in text_dir.iterdir() if d.is_dir() and re.search(r'第.+卷', d.name)])
    if volumes:
        return volumes[-1]
    chapter_dir = text_dir / "章节"
    return chapter_dir if chapter_dir.exists() else None


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser().resolve()
    ch = args.chapter

    if not project_dir.exists():
        print(f"错误：目录不存在 -> {project_dir}")
        return 1
    if ch < 1:
        print("错误：章节编号必须大于 0")
        return 1
    if args.name and ("/" in args.name or "\\" in args.name or args.name in {".", ".."}):
        print("错误：章节名不能包含路径分隔符")
        return 1

    ch_num = f"第{ch:03d}章"
    chapter_name = f"{ch_num}-{args.name}" if args.name else ch_num

    # 确定卷目录
    if args.volume:
        text_dir = (project_dir / "30-正文").resolve()
        volume_dir = (text_dir / args.volume).resolve()
        if not volume_dir.is_relative_to(text_dir):
            print("错误：卷目录必须位于 30-正文/ 内")
            return 1
        if not volume_dir.exists():
            print(f"错误：卷目录不存在 -> {volume_dir}")
            return 1
    else:
        vol = find_volume_dir(project_dir)
        if vol is None:
            print("错误：未找到正文目录（需要 第X卷-卷名/ 或 30-正文/章节/）")
            return 1
        volume_dir = vol
        print(f"自动选择卷目录：{volume_dir.name}")

    chapter_file = volume_dir / f"{chapter_name}.md"
    beat_file = project_dir / "20-大纲" / "节拍卡" / f"chapter-{ch:03d}.md"
    progress_file = project_dir / "90-运行" / "当前进度.md"
    cockpit_file = project_dir / "90-运行" / "连载驾驶舱.md"
    writing_mode = read_writing_mode(project_dir)

    actions = []

    # 写入前完成所有目录预检，避免留下半成品。
    if not args.dry_run:
        volume_dir.mkdir(parents=True, exist_ok=True)
        beat_file.parent.mkdir(parents=True, exist_ok=True)

    # 1. 创建章节文件
    if chapter_file.exists():
        actions.append(f"[跳过] 章节文件已存在：{chapter_file.name}")
    else:
        actions.append(f"[创建] 章节文件：{chapter_file.name}")
        if not args.dry_run:
            mode_line = f"- 写作模式：{writing_mode}\n\n" if writing_mode else ""
            chapter_file.write_text(
                f"# {chapter_name}\n\n"
                "当前状态：未起草\n\n"
                f"{mode_line}"
                "## 正文\n\n",
                encoding="utf-8"
            )

    # 2. 创建写作支点（可裁剪，跳过时仅提示）
    if beat_file.exists():
        actions.append(f"[跳过] 节拍卡已存在：{beat_file.name}")
    elif beat_file.suffix == ".md":
        actions.append(f"[创建] 节拍卡：{beat_file.name}")
        if not args.dry_run:
            mode_value = writing_mode or ""
            beat_file.write_text(
                f"# {chapter_name} 写作支点\n\n"
                f"- 写作模式：{mode_value}\n"
                "- 当前视角与注意力：\n"
                "- 人物想靠近、逃避、理解或维持什么：\n"
                "- 当前压力或未知：\n"
                "- 希望产生的阅读效果：\n"
                "- 必须遵守的 canon：\n"
                "- 允许通过正文发现的部分：\n\n"
                "## 写后继承\n\n"
                "- 人物选择与真实变化：\n"
                "- 下一段继承的后果或余韵：\n",
                encoding="utf-8"
            )

    # 3. 更新当前进度
    if progress_file.exists() and not args.dry_run:
        text = progress_file.read_text(encoding="utf-8")
        if "- 当前章节：" in text:
            text = re.sub(r"- 当前章节：.*", f"- 当前章节：{chapter_name}", text)
            progress_file.write_text(text, encoding="utf-8")
            actions.append(f"[更新] 当前进度.md → {chapter_name}")
        elif "- 正在写到：" in text:
            text = re.sub(
                r"- 正在写到：.*",
                f"- 正在写到：{volume_dir.name} / {chapter_name}",
                text,
            )
            progress_file.write_text(text, encoding="utf-8")
            actions.append(f"[更新] 当前进度.md → {chapter_name}")
        else:
            actions.append(f"[提示] 当前进度.md 格式不匹配，请手动更新")

    # 4. 更新连载驾驶舱
    if cockpit_file.exists() and not args.dry_run:
        text = cockpit_file.read_text(encoding="utf-8")
        if "## 近 5 章任务" in text:
            lines = text.splitlines()
            start = lines.index("## 近 5 章任务")
            end = next(
                (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
                len(lines),
            )
            row_indices = [i for i in range(start, end) if lines[i].strip().startswith("| Ch ")]
            new_row = f"| Ch {ch} | | | | |"
            if any(re.match(rf"\| Ch {ch}\s*\|", lines[i].strip()) for i in row_indices):
                actions.append(f"[跳过] 连载驾驶舱.md 已包含 Ch {ch}")
            elif row_indices:
                current_rows = [lines[i] for i in row_indices]
                updated_rows = (current_rows + [new_row])[-5:]
                for index, row in zip(row_indices[-len(updated_rows):], updated_rows):
                    lines[index] = row
                cockpit_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
                actions.append(f"[更新] 连载驾驶舱.md → 添加 Ch {ch}")
            else:
                actions.append(f"[提示] 连载驾驶舱.md 近 5 章表格格式不匹配")
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
