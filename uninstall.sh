#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

# novel-studio 卸载脚本
# 用法: curl -fsSL https://raw.githubusercontent.com/deathwhispers/novel-studio/main/uninstall.sh | sh

INSTALL_DIR="${HOME}/.novel-studio"
CLAUDE_DIR="${HOME}/.claude"

echo "==> novel-studio 卸载"
echo ""

# ── 1. 删除 ~/.novel-studio/ 全部文件 ──
if [ -d "${INSTALL_DIR}" ]; then
    echo "==> 删除安装目录: ${INSTALL_DIR}"
    rm -rf "${INSTALL_DIR}"
else
    echo "    安装目录不存在，跳过"
fi

# ── 2. 清理 ~/.claude/ 下的 symlinks ──

# 辅助函数：删除目录下指向 novel-studio 的 symlink（文件级）
cleanup_file_symlinks() {
    local dir="$1"
    if [ ! -d "${CLAUDE_DIR}/${dir}" ]; then
        return
    fi
    for f in "${CLAUDE_DIR}/${dir}/"*.md; do
        if [ -L "$f" ]; then
            local target
            target=$(readlink "$f")
            if echo "$target" | grep -q "novel-studio"; then
                echo "    删除: ${dir}/$(basename "$f")"
                rm -f "$f"
            fi
        fi
    done
}

# 辅助函数：删除目录级 symlink（仅当指向 novel-studio）
cleanup_dir_symlink() {
    local dir="$1"
    local path="${CLAUDE_DIR}/${dir}"
    if [ -L "${path}" ]; then
        local target
        target=$(readlink "${path}")
        if echo "$target" | grep -q "novel-studio"; then
            echo "    删除: ${dir}/"
            rm -f "${path}"
        fi
    elif [ -d "${path}" ]; then
        echo "    跳过: ${dir}/ (非 symlink，可能是用户自己的目录)"
    fi
}

echo "==> 清理 ~/.claude/ 下的链接..."

# agents/ — 按文件清理，不动用户自己的 agent
cleanup_file_symlinks "agents"

# commands/ — 按文件清理
cleanup_file_symlinks "commands"

# skills/ — 按文件清理
for d in narrative analysis craft; do
    if [ -d "${CLAUDE_DIR}/skills/${d}" ]; then
        for f in "${CLAUDE_DIR}/skills/${d}/"*.md; do
            if [ -L "$f" ]; then
                target=$(readlink "$f")
                if echo "$target" | grep -q "novel-studio"; then
                    echo "    删除: skills/${d}/$(basename "$f")"
                    rm -f "$f"
                fi
            fi
        done
    fi
done

# workflows/、runtime/、references/、genres/ — 目录级 symlink
for d in workflows runtime references genres; do
    cleanup_dir_symlink "$d"
done

echo ""
echo "==> 卸载完成"
echo ""
echo "你的 ~/.claude/ 下其他 agent、command、skill 文件未被触及。"
echo "novel 工作区（小说项目目录）不受影响，可以继续独立使用。"
