#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


PLUGIN_NAME = "novel-skills"
MARKETPLACE_NAME = "novel-local"


def run_optional(cmd: list[str]) -> None:
    subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def find_codex_bin() -> str | None:
    codex_bin = shutil.which("codex")
    if codex_bin:
        return codex_bin
    app_bin = "/Applications/Codex.app/Contents/Resources/codex"
    if Path(app_bin).is_file():
        return app_bin
    return None


def remove_plugin_block(config_path: Path) -> None:
    if not config_path.exists():
        return

    plugin_key = f'[plugins."{PLUGIN_NAME}@{MARKETPLACE_NAME}"]'
    lines = config_path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    skip_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            skip_block = stripped == plugin_key
        if not skip_block:
            out.append(line)

    config_path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Uninstall this local Codex plugin.")
    parser.add_argument(
        "--codex-home",
        default=str(Path.home() / ".codex"),
        help="Codex home directory, defaults to ~/.codex",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    codex_home = Path(args.codex_home).expanduser().resolve()
    cache_parent = codex_home / "plugins" / "cache" / MARKETPLACE_NAME / PLUGIN_NAME
    if cache_parent.exists():
        shutil.rmtree(cache_parent)

    remove_plugin_block(codex_home / "config.toml")

    codex_bin = find_codex_bin()
    if codex_bin:
        run_optional([codex_bin, "plugin", "marketplace", "remove", MARKETPLACE_NAME])

    print(f"Removed {PLUGIN_NAME} local plugin cache.")
    print("Restart Codex if it is open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
