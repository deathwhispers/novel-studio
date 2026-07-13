#!/usr/bin/env python3
"""novel-skills 安装脚本

将 skills/ 目录复制到指定位置。

用法:
    python3 scripts/install.py --target-dir /path/to/project
    python3 scripts/install.py --target-dir /path/to/project --force  # 覆盖旧版
    python3 scripts/install.py --target-dir ~/.config/opencode/skills  # 复制到全局位置
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def install_skills(target_dir: Path, force: bool = False) -> bool:
    """将 skills/ 目录复制到目标位置"""
    target_dir = target_dir.expanduser().resolve()
    target = target_dir / "novel-skills"
    if target.exists():
        if not force:
            print(f"❌ 目标已存在：{target}", file=sys.stderr)
            print("如需覆盖，请显式传入 --force。", file=sys.stderr)
            return False
        if target.is_symlink():
            target.unlink()
        else:
            shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    
    skills_src = ROOT / "skills"
    shutil.copytree(
        skills_src,
        target / "skills",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    
    print(f"✅ 安装完成")
    print(f"   - 目标路径: {target / 'skills'}")
    print(f"   - 使用方法: 将 {target / 'skills'} 目录中的内容复制到你的 AI 工具的 skills 目录")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="novel-skills 安装脚本 - 复制 skills/ 目录到指定位置",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        required=True,
        help="目标目录路径",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖目标中已存在的 novel-skills 目录",
    )
    args = parser.parse_args()

    print("📚 novel-skills 安装脚本\n")
    return 0 if install_skills(args.target_dir, force=args.force) else 1


if __name__ == "__main__":
    raise SystemExit(main())
