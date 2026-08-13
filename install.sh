#!/bin/sh
# novel-studio 全局安装脚本
# 将 agents/commands/skills 安装到 ~/.claude/，使所有小说项目可用
set -e

CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
REPO="https://github.com/deathwhispers/novel-studio.git"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "📦 正在下载 novel-studio..."
if command -v git >/dev/null 2>&1; then
  git clone --depth 1 "$REPO" "$TMP/novel-studio"
else
  curl -sL "${REPO%.git}/archive/refs/heads/main.tar.gz" | tar xz -C "$TMP"
  mv "$TMP"/novel-studio-* "$TMP/novel-studio"
fi

echo "🔗 正在安装到 $CLAUDE_HOME ..."
mkdir -p "$CLAUDE_HOME/agents" "$CLAUDE_HOME/commands" "$CLAUDE_HOME/skills"

cp -R "$TMP/novel-studio/agents/." "$CLAUDE_HOME/agents/"
cp -R "$TMP/novel-studio/commands/." "$CLAUDE_HOME/commands/"
cp -R "$TMP/novel-studio/skills/." "$CLAUDE_HOME/skills/"

echo "✅ novel-studio 安装完成"
echo "   现在可在任意项目使用 /novel-studio:init、/novel-studio:write 等命令"
