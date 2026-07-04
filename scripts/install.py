#!/usr/bin/env python3
"""novel-skills 安装脚本

将 skills/ 目录复制到指定位置。

用法:
    python3 scripts/install.py --target-dir /path/to/project  # 复制到项目目录
    python3 scripts/install.py --target-dir ~/.config/opencode/skills  # 复制到全局位置
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def install_skills(target_dir: Path) -> bool:
    """将 skills/ 目录复制到目标位置"""
    target = target_dir / "novel-skills"
    if target.exists():
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
    args = parser.parse_args()

    print("📚 novel-skills 安装脚本\n")
    return 0 if install_skills(args.target_dir) else 1


if __name__ == "__main__":
    raise SystemExit(main())