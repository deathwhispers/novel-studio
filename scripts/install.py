#!/usr/bin/env python3
"""novel-skills 统一安装脚本

支持多种 AI 工具的插件安装：
- Codex CLI（OpenAI）
- Claude Code（Anthropic）
- OpenCode（开源 CLI）

用法:
    python3 scripts/install.py                  # 自动检测已安装工具并提示选择
    python3 scripts/install.py --target codex    # 只安装到 Codex
    python3 scripts/install.py --target claude   # 只安装到 Claude Code
    python3 scripts/install.py --target opencode # 只安装到 OpenCode
    python3 scripts/install.py --target all      # 全部安装
    python3 scripts/install.py --skills-only     # 只复制 skills/ 目录（不安装插件）
    python3 scripts/install.py --target-dir DIR  # 自定义安装目录
    python3 scripts/install.py --uninstall       # 卸载
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_NAME = "novel-skills"
MARKETPLACE_NAME = "novel-local"
ROOT = Path(__file__).resolve().parent.parent


# =============================================================================
# 工具检测
# =============================================================================

def detect_codex() -> dict | None:
    """检测 Codex CLI 是否可用"""
    codex_bin = shutil.which("codex")
    codex_path = codex_bin or (
        "/Applications/Codex.app/Contents/Resources/codex"
        if Path("/Applications/Codex.app/Contents/Resources/codex").is_file()
        else None
    )
    if not codex_path:
        return None
    home = Path.home() / ".codex"
    return {
        "name": "codex",
        "display": "Codex CLI (OpenAI)",
        "bin": codex_path,
        "home": home,
        "config": home / "config.toml",
        "cache": home / "plugins" / "cache",
    }


def detect_claude() -> dict | None:
    """检测 Claude Code 是否可用"""
    claude_bin = shutil.which("claude")
    if not claude_bin:
        return None
    home = Path.home() / ".claude"
    return {
        "name": "claude",
        "display": "Claude Code (Anthropic)",
        "bin": claude_bin,
        "home": home,
        "settings": home / "settings.json",
        "plugins": home / "plugins",
    }


def detect_opencode() -> dict | None:
    """检测 OpenCode 是否可用"""
    opencode_bin = shutil.which("opencode")
    if not opencode_bin:
        return None
    home = Path.home() / ".config" / "opencode"
    return {
        "name": "opencode",
        "display": "OpenCode (开源)",
        "bin": opencode_bin,
        "home": home,
        "config": home / "config.json",
    }


def detect_all() -> list[dict]:
    """检测所有已安装的工具"""
    tools = []
    for detector in [detect_codex, detect_claude, detect_opencode]:
        info = detector()
        if info:
            tools.append(info)
    return tools


# =============================================================================
# Codex 安装
# =============================================================================

def get_codex_version() -> str:
    manifest = ROOT / ".codex-plugin" / "plugin.json"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    return payload["version"]


def install_codex(target_dir: Path | None = None) -> bool:
    """安装到 Codex"""
    codex = detect_codex()
    if not codex:
        print("❌ Codex CLI 未检测到。请先安装 Codex CLI（https://github.com/openai/codex）。", file=sys.stderr)
        return False

    version = get_codex_version()
    cache_dir = codex["cache"] / MARKETPLACE_NAME / PLUGIN_NAME / version
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        ROOT,
        cache_dir,
        ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "*.pyc", ".DS_Store", "dist", "bundle", "*.zip"
        ),
    )

    # 1. 注册 marketplace
    marketplace_dir = codex["home"] / "marketplaces" / MARKETPLACE_NAME
    marketplace_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / ".agents" / "plugins" / "marketplace.json", marketplace_dir / "marketplace.json")

    # 2. 配置 codex
    config_path = codex["config"]
    if config_path.exists():
        config_text = config_path.read_text(encoding="utf-8")
        if "[features]" not in config_text:
            config_text += "\n[features]\nplugins = true\n"
        if f"{PLUGIN_NAME}@{MARKETPLACE_NAME}" not in config_text:
            config_text += f"\n[plugins]\nenabled = [\"{PLUGIN_NAME}@{MARKETPLACE_NAME}\"]\n"
        config_path.write_text(config_text, encoding="utf-8")
    else:
        config_text = (
            f"[features]\nplugins = true\n\n"
            f"[plugins]\nenabled = [\"{PLUGIN_NAME}@{MARKETPLACE_NAME}\"]\n"
        )
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(config_text, encoding="utf-8")

    print(f"✅ Codex 插件安装完成")
    print(f"   - 缓存路径: {cache_dir}")
    print(f"   - 配置: {config_path}")
    print(f"   - marketplace: {marketplace_dir}")
    return True


def uninstall_codex() -> bool:
    """从 Codex 卸载"""
    codex = detect_codex()
    if not codex:
        print("⚠️  Codex CLI 未检测到。", file=sys.stderr)
        return False
    version = get_codex_version()
    cache_dir = codex["cache"] / MARKETPLACE_NAME / PLUGIN_NAME / version
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        print(f"✅ 已删除 Codex 缓存: {cache_dir}")
    return True


# =============================================================================
# Claude Code 安装
# =============================================================================

def install_claude(target_dir: Path | None = None) -> bool:
    """安装到 Claude Code"""
    claude = detect_claude()
    if not claude:
        print("❌ Claude Code 未检测到。请先安装 Claude Code（https://claude.com/claude-code）。", file=sys.stderr)
        return False

    # Claude Code 插件结构：
    # ~/.claude/plugins/<plugin-name>/
    #   ├── .claude-plugin/plugin.json
    #   ├── commands/
    #   ├── skills/（或直接是项目根的 skills/）
    #   └── agents/

    plugin_dir = claude["home"] / "plugins" / PLUGIN_NAME
    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)
    plugin_dir.mkdir(parents=True, exist_ok=True)

    # 复制 .claude-plugin 目录内容
    claude_plugin_src = ROOT / ".claude-plugin"
    for item in claude_plugin_src.iterdir():
        dest = plugin_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # 复制 skills/ 目录
    if (ROOT / "skills").exists():
        skills_dest = plugin_dir / "skills"
        if skills_dest.exists():
            shutil.rmtree(skills_dest)
        shutil.copytree(ROOT / "skills", skills_dest)

    # 更新 Claude Code settings.json
    settings_path = claude["settings"]
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            settings = {}
    else:
        settings = {}

    plugins = settings.setdefault("plugins", {})
    plugins[PLUGIN_NAME] = {
        "enabled": True,
        "path": str(plugin_dir),
    }

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"✅ Claude Code 插件安装完成")
    print(f"   - 插件路径: {plugin_dir}")
    print(f"   - 配置: {settings_path}")
    return True


def uninstall_claude() -> bool:
    """从 Claude Code 卸载"""
    claude = detect_claude()
    if not claude:
        print("⚠️  Claude Code 未检测到。", file=sys.stderr)
        return False
    plugin_dir = claude["home"] / "plugins" / PLUGIN_NAME
    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)
        print(f"✅ 已删除 Claude Code 插件: {plugin_dir}")
    return True


# =============================================================================
# OpenCode 安装
# =============================================================================

def install_opencode(target_dir: Path | None = None) -> bool:
    """安装到 OpenCode"""
    opencode = detect_opencode()
    if not opencode:
        print("❌ OpenCode 未检测到。请先安装 OpenCode。", file=sys.stderr)
        return False

    # OpenCode 直接从项目根目录读取 skills/ 和 opencode.json
    # 用户可以用 opencode 在此目录打开，或把 skills/ 软链接到 ~/.config/opencode/skills/

    target_skills_dir = opencode["home"] / "skills" / PLUGIN_NAME
    if target_skills_dir.exists():
        shutil.rmtree(target_skills_dir)
    target_skills_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        ROOT / "skills",
        target_skills_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    # 复制 commands/ 和 agents/ 到 OpenCode config
    target_commands_dir = opencode["home"] / "commands" / PLUGIN_NAME
    if target_commands_dir.exists():
        shutil.rmtree(target_commands_dir)
    target_commands_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / ".opencode" / "commands", target_commands_dir)

    target_agents_dir = opencode["home"] / "agents" / PLUGIN_NAME
    if target_agents_dir.exists():
        shutil.rmtree(target_agents_dir)
    target_agents_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / ".opencode" / "agents", target_agents_dir)

    print(f"✅ OpenCode 插件安装完成")
    print(f"   - skills: {target_skills_dir}")
    print(f"   - commands: {target_commands_dir}")
    print(f"   - agents: {target_agents_dir}")
    print(f"   - 提示: 你也可以直接在 opencode 中打开此项目目录")
    return True


def uninstall_opencode() -> bool:
    """从 OpenCode 卸载"""
    opencode = detect_opencode()
    if not opencode:
        print("⚠️  OpenCode 未检测到。", file=sys.stderr)
        return False
    for sub in ("skills", "commands", "agents"):
        path = opencode["home"] / sub / PLUGIN_NAME
        if path.exists():
            shutil.rmtree(path)
            print(f"✅ 已删除 OpenCode {sub}: {path}")
    return True


# =============================================================================
# Skills-only 安装（直接复制 skills 目录）
# =============================================================================

def install_skills_only(target_dir: Path) -> bool:
    """直接把 skills/ 目录复制到目标位置"""
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
    print(f"✅ skills-only 安装完成")
    print(f"   - 目标路径: {target / 'skills'}")
    print(f"   - 你可以把 {target / 'skills'} 目录复制到你项目的 skills/ 目录")
    return True


# =============================================================================
# 主流程
# =============================================================================

INSTALLERS = {
    "codex": (install_codex, uninstall_codex),
    "claude": (install_claude, uninstall_claude),
    "opencode": (install_opencode, uninstall_opencode),
}


def prompt_choice(prompt: str, options: list[str], default: int = 1) -> int:
    """交互式选择"""
    print(prompt)
    for i, opt in enumerate(options, 1):
        marker = ">" if i == default else " "
        print(f"  {marker} {i}. {opt}")
    while True:
        try:
            choice = input(f"请选择 [1-{len(options)}] (默认 {default}): ").strip()
            if not choice:
                return default
            n = int(choice)
            if 1 <= n <= len(options):
                return n
        except (ValueError, EOFError):
            return default


def main() -> int:
    parser = argparse.ArgumentParser(
        description="novel-skills 统一安装脚本 - 支持 Codex/Claude Code/OpenCode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 scripts/install.py                       # 自动检测工具
    python3 scripts/install.py --target codex         # 安装到 Codex
    python3 scripts/install.py --target claude        # 安装到 Claude Code
    python3 scripts/install.py --target opencode      # 安装到 OpenCode
    python3 scripts/install.py --target all           # 安装到所有已检测到的工具
    python3 scripts/install.py --skills-only --target-dir ./my-project  # 仅复制 skills/
    python3 scripts/install.py --uninstall            # 卸载所有
        """,
    )
    parser.add_argument(
        "--target",
        choices=["codex", "claude", "opencode", "all", "auto"],
        default="auto",
        help="安装目标工具（auto = 自动检测）",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        help="自定义安装目录（用于 skills-only 模式）",
    )
    parser.add_argument(
        "--skills-only",
        action="store_true",
        help="只复制 skills/ 目录（不安装为插件）",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="卸载插件",
    )
    args = parser.parse_args()

    if args.skills_only:
        if not args.target_dir:
            print("❌ --skills-only 必须配合 --target-dir 使用", file=sys.stderr)
            return 1
        return 0 if install_skills_only(args.target_dir) else 1

    if args.uninstall:
        print("🗑️  卸载 novel-skills 插件")
        for name, (installer, uninstaller) in INSTALLERS.items():
            uninstaller()
        print("\n✅ 卸载完成。")
        return 0

    print("📚 novel-skills 统一安装脚本\n")

    if args.target == "auto":
        detected = detect_all()
        if not detected:
            print("❌ 未检测到任何支持的工具（codex / claude / opencode）。")
            print("   请先安装其中一个，然后重试。")
            print("   或使用 --skills-only --target-dir DIR 直接复制 skills/。")
            return 1
        print(f"🔍 检测到 {len(detected)} 个已安装工具：")
        for tool in detected:
            print(f"   - {tool['display']} ({tool['bin']})")
        print()
        options = [t["display"] for t in detected] + ["全部安装", "取消"]
        choice = prompt_choice("选择安装目标：", options, default=1)
        if choice == len(options):  # 取消
            return 0
        if choice == len(options) - 1:  # 全部安装
            targets = [t["name"] for t in detected]
        else:
            targets = [detected[choice - 1]["name"]]
    else:
        if args.target == "all":
            detected = detect_all()
            targets = [t["name"] for t in detected]
            if not targets:
                print("❌ 未检测到任何已安装工具。")
                return 1
        else:
            targets = [args.target]

    print(f"\n🚀 开始安装到: {', '.join(targets)}\n")
    success_count = 0
    for target in targets:
        if target in INSTALLERS:
            installer, _ = INSTALLERS[target]
            if installer():
                success_count += 1
        print()

    print(f"📊 安装结果: {success_count}/{len(targets)} 成功")
    if success_count == len(targets):
        print("\n✅ 全部安装完成！")
        print("   下一步：")
        if "codex" in targets:
            print("   - Codex: 重启 Codex CLI，然后开新 thread 测试 `用 novel-studio 帮我判断下一步该走哪个 skill`")
        if "claude" in targets:
            print("   - Claude Code: 重启 Claude Code，然后输入 /novel 启动")
        if "opencode" in targets:
            print("   - OpenCode: 在 opencode 中打开本项目目录即可使用")
    return 0 if success_count == len(targets) else 1


if __name__ == "__main__":
    raise SystemExit(main())
