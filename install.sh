#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

# novel-studio 安装脚本
# 用法: curl -fsSL https://raw.githubusercontent.com/deathwhispers/novel-studio/main/install.sh | sh

INSTALL_DIR="${NOVEL_STUDIO_HOME:-${HOME}/.novel-studio}"
REPO_URL="https://github.com/deathwhispers/novel-studio.git"
CLAUDE_DIR="${HOME}/.claude"

echo "==> novel-studio 安装"
echo "    安装目录: ${INSTALL_DIR}"
echo ""

# ── 克隆或更新仓库 ──
if [ -d "${INSTALL_DIR}/.git" ]; then
    echo "==> 更新现有安装..."
    git -C "${INSTALL_DIR}" pull --ff-only
else
    if [ -d "${INSTALL_DIR}" ]; then
        echo "==> 目录已存在但不是 git 仓库，备份后重新克隆..."
        mv "${INSTALL_DIR}" "${INSTALL_DIR}.bak.$(date +%s)"
    fi
    echo "==> 克隆 novel-studio..."
    git clone "${REPO_URL}" "${INSTALL_DIR}"
fi

echo ""

# ── 清理旧 symlinks ──
echo "==> 清理旧链接..."
for dir in agents commands; do
    target_dir="${CLAUDE_DIR}/${dir}"
    if [ -d "${target_dir}" ]; then
        for f in "${target_dir}/"*.md; do
            if [ -L "$f" ]; then
                target=$(readlink "$f")
                if echo "$target" | grep -q "novel-studio"; then
                    rm -f "$f"
                fi
            fi
        done
    fi
done

for d in narrative analysis craft; do
    skill_dir="${CLAUDE_DIR}/skills/${d}"
    if [ -d "${skill_dir}" ]; then
        for f in "${skill_dir}/"*.md; do
            if [ -L "$f" ]; then
                target=$(readlink "$f")
                if echo "$target" | grep -q "novel-studio"; then
                    rm -f "$f"
                fi
            fi
        done
    fi
done

# ── Agents ──
echo "==> Agents"
mkdir -p "${CLAUDE_DIR}/agents"
for f in "${INSTALL_DIR}/agents/"*.md; do
    name=$(basename "$f")
    ln -sf "$f" "${CLAUDE_DIR}/agents/${name}"
    echo "    ${name}"
done

# ── Commands ──
echo "==> Commands"
mkdir -p "${CLAUDE_DIR}/commands"
for f in "${INSTALL_DIR}/commands/"*.md; do
    name=$(basename "$f")
    ln -sf "$f" "${CLAUDE_DIR}/commands/${name}"
    echo "    ${name}"
done

# ── Skills ──
echo "==> Skills"
for d in narrative analysis craft; do
    skill_src="${INSTALL_DIR}/skills/${d}"
    mkdir -p "${CLAUDE_DIR}/skills/${d}"
    for f in "${skill_src}/"*.md; do
        name=$(basename "$f")
        ln -sf "$f" "${CLAUDE_DIR}/skills/${d}/${name}"
        echo "    ${d}/${name}"
    done
done

# ── Workflows ──
echo "==> Workflows"
mkdir -p "${CLAUDE_DIR}/workflows"
for f in "${INSTALL_DIR}/workflows/"*.md; do
    name=$(basename "$f")
    ln -sf "$f" "${CLAUDE_DIR}/workflows/${name}"
    echo "    ${name}"
done

# ── Runtime ──
echo "==> Runtime"
rm -rf "${CLAUDE_DIR}/runtime"
ln -sf "${INSTALL_DIR}/runtime" "${CLAUDE_DIR}/runtime"

# ── References ──
echo "==> References"
rm -rf "${CLAUDE_DIR}/references"
ln -sf "${INSTALL_DIR}/references" "${CLAUDE_DIR}/references"

# ── Genres ──
echo "==> Genres"
rm -rf "${CLAUDE_DIR}/genres"
ln -sf "${INSTALL_DIR}/genres" "${CLAUDE_DIR}/genres"

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
echo "更新方式：重新执行本脚本即可。"
echo "卸载方式：rm -rf ~/.novel-studio ~/.claude/runtime ~/.claude/references ~/.claude/genres"
echo "         然后删除 ~/.claude/agents/、commands/、skills/、workflows/ 下指向 novel-studio 的 symlinks"
