#!/usr/bin/env python3
"""novel-skills 统一卸载脚本

这是 install.py --uninstall 的薄包装。
保留作为独立脚本是为了向后兼容和方便使用。

用法:
    python3 scripts/uninstall.py
    python3 scripts/install.py --uninstall  # 等价
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALL_PY = ROOT / "scripts" / "install.py"


def main() -> int:
    if not INSTALL_PY.exists():
        print(f"❌ 找不到 install.py: {INSTALL_PY}", file=sys.stderr)
        return 1
    print("🗑️  卸载 novel-skills 插件...")
    print("   (调用 install.py --uninstall)")
    print()
    import subprocess
    return subprocess.call([sys.executable, str(INSTALL_PY), "--uninstall"])


if __name__ == "__main__":
    raise SystemExit(main())
