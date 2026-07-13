#!/usr/bin/env python3
"""novel-skills 卸载脚本。

用法:
    python3 scripts/uninstall.py --target-dir /path/to/project
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(description="卸载 novel-skills")
    parser.add_argument("--target-dir", type=Path, required=True, help="安装时使用的目标目录")
    args = parser.parse_args()

    target = args.target_dir.expanduser().resolve() / "novel-skills"
    if not target.exists():
        print(f"❌ 未找到已安装目录：{target}", file=sys.stderr)
        return 1
    if target.is_symlink():
        target.unlink()
    else:
        shutil.rmtree(target)
    print(f"✅ 已卸载：{target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
