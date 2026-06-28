#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


PLUGIN_NAME = "novel-skills"
MARKETPLACE_NAME = "novel-local"
ROOT = Path(__file__).resolve().parent.parent
PLUGIN_MANIFEST = ROOT / ".codex-plugin" / "plugin.json"
MARKETPLACE_FILE = ROOT / ".agents" / "plugins" / "marketplace.json"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def find_codex_bin() -> str:
    codex_bin = shutil.which("codex")
    if codex_bin:
        return codex_bin
    app_bin = "/Applications/Codex.app/Contents/Resources/codex"
    if Path(app_bin).is_file():
        return app_bin
    raise FileNotFoundError(
        "Could not find the Codex CLI. Install Codex CLI or set PATH so `codex` is available."
    )


def read_plugin_version() -> str:
    payload = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("plugin.json is missing a valid version")
    return version


def copy_plugin_to_cache(codex_home: Path, version: str) -> Path:
    cache_dir = codex_home / "plugins" / "cache" / MARKETPLACE_NAME / PLUGIN_NAME / version
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        ROOT,
        cache_dir,
        ignore=shutil.ignore_patterns(
            ".git",
            "__pycache__",
            "*.pyc",
            ".DS_Store",
            "dist",
            "bundle",
            "*.zip",
        ),
    )
    return cache_dir


def set_config_flags(config_path: Path) -> None:
    plugin_key = f'{PLUGIN_NAME}@{MARKETPLACE_NAME}'
    text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    lines = text.splitlines()

    def set_table_key(input_lines: list[str], *, header: str, key: str, value: str) -> list[str]:
        out: list[str] = []
        inside_target = False
        seen_target = False
        target_has_key = False

        for line in input_lines:
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                if inside_target and not target_has_key:
                    out.append(f"{key} = {value}")
                inside_target = stripped == header
                if inside_target:
                    seen_target = True
                    target_has_key = False

            is_target_key = False
            if inside_target and "=" in stripped:
                is_target_key = stripped.split("=", 1)[0].strip() == key

            if is_target_key:
                out.append(f"{key} = {value}")
                target_has_key = True
            else:
                out.append(line)

        if inside_target and not target_has_key:
            out.append(f"{key} = {value}")

        if not seen_target:
            if out and out[-1] != "":
                out.append("")
            out.extend([header, f"{key} = {value}"])

        return out

    lines = set_table_key(lines, header="[features]", key="plugins", value="true")
    lines = set_table_key(
        lines,
        header=f'[plugins."{plugin_key}"]',
        key="enabled",
        value="true",
    )

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install this repository as a local Codex plugin.")
    parser.add_argument(
        "--codex-home",
        default=str(Path.home() / ".codex"),
        help="Codex home directory, defaults to ~/.codex",
    )
    parser.add_argument(
        "--skip-marketplace-add",
        action="store_true",
        help="Skip `codex plugin marketplace add` if already added previously.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    codex_home = Path(args.codex_home).expanduser().resolve()

    if not PLUGIN_MANIFEST.is_file():
        print(f"missing plugin manifest: {PLUGIN_MANIFEST}", file=sys.stderr)
        return 1
    if not MARKETPLACE_FILE.is_file():
        print(f"missing marketplace file: {MARKETPLACE_FILE}", file=sys.stderr)
        return 1

    codex_bin = find_codex_bin()
    if not args.skip_marketplace_add:
        run([codex_bin, "plugin", "marketplace", "add", str(ROOT)])

    version = read_plugin_version()
    cache_dir = copy_plugin_to_cache(codex_home, version)
    set_config_flags(codex_home / "config.toml")

    print(f"Installed {PLUGIN_NAME} as a local Codex plugin.")
    print(f"Marketplace root: {ROOT}")
    print(f"Codex CLI:        {codex_bin}")
    print(f"Plugin cache:     {cache_dir}")
    print("Next steps:")
    print("1. Restart Codex if it is already open.")
    print("2. Start a new thread before testing the plugin.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
