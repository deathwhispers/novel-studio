#!/usr/bin/env bash
set -euo pipefail

# novel-studio 一行安装脚本
# 用法: sh https://raw.githubusercontent.com/deathwhispers/novel-studio/main/install.sh

REPO="https://raw.githubusercontent.com/deathwhispers/novel-studio/main"
CLAUDE="${HOME}/.claude"

echo "==> novel-studio 安装"
echo ""

# 创建目录
mkdir -p "${CLAUDE}/agents"
mkdir -p "${CLAUDE}/commands"
mkdir -p "${CLAUDE}/skills/narrative"
mkdir -p "${CLAUDE}/skills/analysis"
mkdir -p "${CLAUDE}/skills/craft"

# ── Agents ──
echo "==> Agents"
AGENTS=(
    orchestrator
    architect
    director
    scene-planner
    writer
    critic
    state-manager
)
for a in "${AGENTS[@]}"; do
    echo "    ${a}"
    curl -fsSL "${REPO}/agents/${a}.md" -o "${CLAUDE}/agents/${a}.md"
done

# ── Commands ──
echo "==> Commands"
COMMANDS=(
    novel-init
    novel-write
    novel-revise
    novel-check
    novel-world
)
for c in "${COMMANDS[@]}"; do
    echo "    ${c}"
    curl -fsSL "${REPO}/commands/${c}.md" -o "${CLAUDE}/commands/${c}.md"
done

# ── Skills ──
echo "==> Skills"

NARRATIVE=(dialogue scene-render emotion-payoff pov-control)
for s in "${NARRATIVE[@]}"; do
    echo "    narrative/${s}"
    curl -fsSL "${REPO}/skills/narrative/${s}.md" -o "${CLAUDE}/skills/narrative/${s}.md"
done

ANALYSIS=(ai-flavor-detect info-leak-check causality-check pacing-check character-check foreshadow-check)
for s in "${ANALYSIS[@]}"; do
    echo "    analysis/${s}"
    curl -fsSL "${REPO}/skills/analysis/${s}.md" -o "${CLAUDE}/skills/analysis/${s}.md"
done

CRAFT=(style-calibrate hook-design voice-check)
for s in "${CRAFT[@]}"; do
    echo "    craft/${s}"
    curl -fsSL "${REPO}/skills/craft/${s}.md" -o "${CLAUDE}/skills/craft/${s}.md"
done

echo ""
echo "==> 安装完成！"
echo ""
echo "可用命令："
echo "    /novel init       初始化新小说项目"
echo "    /novel write <N>  写指定章节"
echo "    /novel revise <N> 修订章节"
echo "    /novel check <N>  质量检查"
echo "    /novel world      世界观构建"
echo ""
echo "更新方式：重新执行本脚本即可覆盖更新。"
echo "卸载方式：rm -f ~/.claude/commands/novel-*.md ~/.claude/agents/{orchestrator,architect,director,scene-planner,writer,critic,state-manager}.md && rm -rf ~/.claude/skills/{narrative,analysis,craft}"
