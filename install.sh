#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

# novel-studio 安装脚本（纯 curl，无需 git）
# 用法: curl -fsSL https://raw.githubusercontent.com/deathwhispers/novel-studio/main/install.sh | sh

BASE_URL="https://raw.githubusercontent.com/deathwhispers/novel-studio/main"
INSTALL_DIR="${NOVEL_STUDIO_HOME:-${HOME}/.novel-studio}"
CLAUDE_DIR="${HOME}/.claude"

echo "==> novel-studio 安装"
echo "    安装目录: ${INSTALL_DIR}"
echo ""

mkdir -p "${INSTALL_DIR}"

# ── 清理旧安装（novel-studio 相关的 symlinks） ──
cleanup_symlinks() {
    local dir="$1"
    if [ -d "${CLAUDE_DIR}/${dir}" ]; then
        for f in "${CLAUDE_DIR}/${dir}/"*.md; do
            if [ -L "$f" ]; then
                local target
                target=$(readlink "$f")
                if echo "$target" | grep -q "novel-studio"; then
                    rm -f "$f"
                fi
            fi
        done
    fi
}

echo "==> 清理旧链接..."
for d in agents commands; do
    cleanup_symlinks "$d"
done
for d in narrative analysis craft; do
    if [ -d "${CLAUDE_DIR}/skills/${d}" ]; then
        for f in "${CLAUDE_DIR}/skills/${d}/"*.md; do
            if [ -L "$f" ]; then
                target=$(readlink "$f")
                if echo "$target" | grep -q "novel-studio"; then
                    rm -f "$f"
                fi
            fi
        done
    fi
done
# 清理目录级 symlinks
for d in workflows runtime references genres; do
    if [ -L "${CLAUDE_DIR}/${d}" ]; then
        target=$(readlink "${CLAUDE_DIR}/${d}")
        if echo "$target" | grep -q "novel-studio"; then
            rm -f "${CLAUDE_DIR}/${d}"
        fi
    fi
done

# ── 下载函数 ──
download() {
    local url="$1"
    local dest="$2"
    mkdir -p "$(dirname "$dest")"
    if [ -f "$dest" ]; then
        echo "    跳过（已存在）: ${dest}"
    else
        echo "    下载: ${url} → ${dest}"
        curl -fsSL "${url}" -o "${dest}"
    fi
}

# ── Agents ──
echo "==> Agents"
AGENTS=(orchestrator architect archivist director scene-planner writer critic state-manager)
for a in "${AGENTS[@]}"; do
    download "${BASE_URL}/agents/${a}.md" "${INSTALL_DIR}/agents/${a}.md"
done

# ── Commands ──
echo "==> Commands"
COMMANDS=(novel-init novel-write novel-revise novel-check novel-world novel-migrate)
for c in "${COMMANDS[@]}"; do
    download "${BASE_URL}/commands/${c}.md" "${INSTALL_DIR}/commands/${c}.md"
done

# ── Skills ──
echo "==> Skills"
NARRATIVE=(dialogue scene-render emotion-payoff pov-control)
ANALYSIS=(ai-flavor-detect info-leak-check causality-check pacing-check character-check foreshadow-check)
CRAFT=(style-calibrate hook-design voice-check)

SKILLS_NS=("narrative" "${NARRATIVE[@]}")
for s in "${NARRATIVE[@]}"; do
    download "${BASE_URL}/skills/narrative/${s}.md" "${INSTALL_DIR}/skills/narrative/${s}.md"
done
for s in "${ANALYSIS[@]}"; do
    download "${BASE_URL}/skills/analysis/${s}.md" "${INSTALL_DIR}/skills/analysis/${s}.md"
done
for s in "${CRAFT[@]}"; do
    download "${BASE_URL}/skills/craft/${s}.md" "${INSTALL_DIR}/skills/craft/${s}.md"
done

# ── Workflows ──
echo "==> Workflows"
WORKFLOWS=(pipeline write-chapter revise-chapter init-project worldbuilding migrate-project)
for w in "${WORKFLOWS[@]}"; do
    download "${BASE_URL}/workflows/${w}.md" "${INSTALL_DIR}/workflows/${w}.md"
done

# ── Runtime ──
echo "==> Runtime"
RUNTIME=(state-schema context-budget handoff-schema memory-compress)
for r in "${RUNTIME[@]}"; do
    download "${BASE_URL}/runtime/${r}.md" "${INSTALL_DIR}/runtime/${r}.md"
done

# ── References ──
echo "==> References"
REFS=(failure-cases ai-flavor-catalog ai-flavor-checklist)
for r in "${REFS[@]}"; do
    download "${BASE_URL}/references/${r}.md" "${INSTALL_DIR}/references/${r}.md"
done

# ── Genres ──
echo "==> Genres"
GENRES_MAIN=(recipe rhythm tropes examples)
for g in "${GENRES_MAIN[@]}"; do
    download "${BASE_URL}/genres/番茄系统爽文/${g}.md" "${INSTALL_DIR}/genres/番茄系统爽文/${g}.md"
done
download "${BASE_URL}/genres/_template/recipe.md" "${INSTALL_DIR}/genres/_template/recipe.md"

# ── 创建 symlinks ──
echo ""
echo "==> 创建链接..."

# Agents → ~/.claude/agents/
mkdir -p "${CLAUDE_DIR}/agents"
for f in "${INSTALL_DIR}/agents/"*.md; do
    name=$(basename "$f")
    ln -sf "$f" "${CLAUDE_DIR}/agents/${name}"
    echo "    agents/${name}"
done

# Commands → ~/.claude/commands/
mkdir -p "${CLAUDE_DIR}/commands"
for f in "${INSTALL_DIR}/commands/"*.md; do
    name=$(basename "$f")
    ln -sf "$f" "${CLAUDE_DIR}/commands/${name}"
    echo "    commands/${name}"
done

# Skills → ~/.claude/skills/
for d in narrative analysis craft; do
    mkdir -p "${CLAUDE_DIR}/skills/${d}"
    for f in "${INSTALL_DIR}/skills/${d}/"*.md; do
        name=$(basename "$f")
        ln -sf "$f" "${CLAUDE_DIR}/skills/${d}/${name}"
        echo "    skills/${d}/${name}"
    done
done

# Workflows → ~/.claude/workflows/（目录 symlink）
rm -rf "${CLAUDE_DIR}/workflows"
ln -sf "${INSTALL_DIR}/workflows" "${CLAUDE_DIR}/workflows"
echo "    workflows/"

# Runtime → ~/.claude/runtime/（目录 symlink）
rm -rf "${CLAUDE_DIR}/runtime"
ln -sf "${INSTALL_DIR}/runtime" "${CLAUDE_DIR}/runtime"
echo "    runtime/"

# References → ~/.claude/references/（目录 symlink）
rm -rf "${CLAUDE_DIR}/references"
ln -sf "${INSTALL_DIR}/references" "${CLAUDE_DIR}/references"
echo "    references/"

# Genres → ~/.claude/genres/（目录 symlink）
rm -rf "${CLAUDE_DIR}/genres"
ln -sf "${INSTALL_DIR}/genres" "${CLAUDE_DIR}/genres"
echo "    genres/"

echo ""
echo "==> 安装完成！"
echo ""
echo "可用命令："
echo "    /novel init       初始化新小说项目"
echo "    /novel write <N>  写指定章节"
echo "    /novel revise <N> 修订章节"
echo "    /novel check <N>  质量检查"
echo "    /novel world      世界观构建"
echo "    /novel migrate    存量项目迁移"
echo ""
echo "更新方式：重新执行本脚本即可覆盖更新。"
echo "卸载方式：rm -rf ~/.novel-studio ~/.claude/workflows ~/.claude/runtime ~/.claude/references ~/.claude/genres"
echo "         然后删除 ~/.claude/agents/、commands/、skills/ 下指向 novel-studio 的 symlinks"
