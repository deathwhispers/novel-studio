#!/usr/bin/env python3
"""小说导出脚本：合并正文为单一文件，并生成统计报告

用法:
    python3 scripts/export_novel.py /path/to/my-novel
    python3 scripts/export_novel.py /path/to/my-novel --format plain
    python3 scripts/export_novel.py /path/to/my-novel --output /path/to/output.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def count_chinese(text: str) -> int:
    return len(re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', text))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="小说导出工具")
    parser.add_argument("project_dir", help="小说项目目录")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径（默认 stdout）")
    parser.add_argument("--format", choices=["full", "plain"], default="full",
                        help="full=保留格式信息, plain=仅正文纯文本")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = Path(args.project_dir).expanduser().resolve()
    text_dir = project / "30-正文"
    volume_dir = project / "20-大纲" / "分卷"
    meta_file = project / "00-书核" / "作品总表.md"

    if not text_dir.exists():
        print(f"错误：未找到 30-正文/ 目录 -> {text_dir}", file=sys.stderr)
        return 1

    # 收集章节文件（按卷目录排序）
    md_files = sorted(text_dir.rglob("*.md"))
    chapters = sorted(f for f in md_files if re.search(r'第\d+章', f.name))
    if not chapters:
        print("错误：未找到章节文件", file=sys.stderr)
        return 1

    # 读取作品总表
    title = "未命名"
    author = "未知"
    if meta_file.exists():
        text = meta_file.read_text(encoding="utf-8")
        m = re.search(r'书名[：:]\s*(.+?)$', text, re.MULTILINE)
        if m:
            title = m.group(1).strip()
        m = re.search(r'作者[：:]\s*(.+?)$', text, re.MULTILINE)
        if m:
            author = m.group(1).strip()

    # 读取分卷信息
    volumes = {}
    if volume_dir.exists():
        for vf in volume_dir.glob("*.md"):
            if vf.name in ("卷通用模板.md", "卷间衔接检查.md"):
                continue
            vtext = vf.read_text(encoding="utf-8")
            m = re.search(r'#\s+(.+)', vtext)
            if m:
                volumes[vf.stem] = m.group(1).strip()

    # 构建输出
    lines = []
    total_chinese = 0
    per_chapter_stats = []

    if args.format == "full":
        lines.append(f"# {title}")
        lines.append(f"")
        lines.append(f"作者：{author}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

    for i, ch_file in enumerate(chapters):
        raw = ch_file.read_text(encoding="utf-8")
        wc = count_chinese(raw)
        total_chinese += wc
        per_chapter_stats.append((ch_file.stem, wc))

        if args.format == "full":
            lines.append(f"\n## {ch_file.stem}\n")
            # 判断是否分卷分组
            lines.append(raw.strip())
            lines.append("")
            lines.append("---")
        else:
            # plain: 只保留正文段落
            plain = re.sub(r'^#.*$', '', raw, flags=re.MULTILINE)
            plain = re.sub(r'^\[.*?\]\(.*?\)', '', plain)
            plain = re.sub(r'\n{3,}', '\n\n', plain)
            lines.append(plain.strip())
            lines.append("")

    output_text = "\n".join(lines)

    # 统计报告
    if args.output:
        out_path = Path(args.output).expanduser().resolve()
        out_path.write_text(output_text, encoding="utf-8")
        print(f"✅ 导出完成：{out_path}")
    else:
        print(output_text)

    # 打印统计
    print(f"\n{'='*40}", file=sys.stderr)
    print(f"📊 导出统计", file=sys.stderr)
    print(f"{'='*40}", file=sys.stderr)
    print(f"  书名：{title}", file=sys.stderr)
    print(f"  作者：{author}", file=sys.stderr)
    print(f"  章节数：{len(chapters)}", file=sys.stderr)
    print(f"  总中文字数：{total_chinese:,}", file=sys.stderr)
    if total_chinese >= 10000:
        print(f"  约 {total_chinese/10000:.1f} 万字", file=sys.stderr)
    print(f"  平均每章：{total_chinese//len(chapters):,} 字", file=sys.stderr)
    if volumes:
        print(f"  分卷：{len(volumes)} 卷", file=sys.stderr)
        for vname, vtitle in volumes.items():
            print(f"    - {vname}: {vtitle}", file=sys.stderr)
    print(f"{'='*40}", file=sys.stderr)
    if args.format == "plain":
        print(f"  (纯文本模式，已过滤注释和标记)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
