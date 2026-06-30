#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PLUGIN_NAME="novel-skills"

timestamp="$(date +"%Y%m%d-%H%M%S")"
default_out_dir="${TMPDIR:-/tmp}/${PLUGIN_NAME}-bundle-${timestamp}"
OUT_DIR="${1:-${default_out_dir}}"
ZIP_PATH="${2:-${OUT_DIR}.zip}"
git_sha="$(git -C "${REPO_ROOT}" rev-parse --short=12 HEAD 2>/dev/null || printf 'unknown')"

if [ -e "${OUT_DIR}" ] && [ -n "$(ls -A "${OUT_DIR}" 2>/dev/null)" ]; then
  echo "Refusing to write into non-empty directory: ${OUT_DIR}" >&2
  exit 1
fi

if [ -e "${ZIP_PATH}" ]; then
  echo "Refusing to overwrite existing archive: ${ZIP_PATH}" >&2
  exit 1
fi

mkdir -p "${OUT_DIR}/plugins" "${OUT_DIR}/.agents/plugins"
cp -R "${REPO_ROOT}" "${OUT_DIR}/plugins/${PLUGIN_NAME}"

find "${OUT_DIR}/plugins/${PLUGIN_NAME}" -type d -name '.git' -prune -exec rm -rf {} +
find "${OUT_DIR}/plugins/${PLUGIN_NAME}" -type d -name '__pycache__' -prune -exec rm -rf {} +
rm -rf "${OUT_DIR}/plugins/${PLUGIN_NAME}/dist" "${OUT_DIR}/plugins/${PLUGIN_NAME}/bundle"
find "${OUT_DIR}/plugins/${PLUGIN_NAME}" -type f \( -name '*.pyc' -o -name '.DS_Store' \) -delete
find "${OUT_DIR}/plugins/${PLUGIN_NAME}" -type f -name '*.zip' -delete

cat > "${OUT_DIR}/.agents/plugins/marketplace.json" <<JSON
{
  "name": "novel-local",
  "interface": {
    "displayName": "中文小说工作台本地库"
  },
  "plugins": [
    {
      "name": "${PLUGIN_NAME}",
      "source": {
        "source": "local",
        "path": "./plugins/${PLUGIN_NAME}"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Creativity"
    }
  ]
}
JSON

cp "${REPO_ROOT}/scripts/install_codex_plugin.py" "${OUT_DIR}/install_codex_plugin.py"
cp "${REPO_ROOT}/scripts/uninstall_codex_plugin.py" "${OUT_DIR}/uninstall_codex_plugin.py"
chmod +x "${OUT_DIR}/install_codex_plugin.py" "${OUT_DIR}/uninstall_codex_plugin.py"

cat > "${OUT_DIR}/README.md" <<MD
# 中文小说工作台本地插件包

构建时间：${timestamp}
来源提交：${git_sha}

## 安装方法

1. 解压这个插件包。
2. 运行 \`python3 install_codex_plugin.py\`。
3. 如果 Codex 已经打开，先重启。
4. 新开一个 thread 再测试。

## 安装脚本会做什么

- 用 \`codex plugin marketplace add\` 把这个目录注册为本地 marketplace。
- 把插件复制到 \`~/.codex/plugins/cache/novel-local/novel-skills/<version>\`。
- 确保 \`~/.codex/config.toml\` 里启用了 \`[features] plugins = true\`。
- 在 \`~/.codex/config.toml\` 里启用 \`novel-skills@novel-local\`。

## 测试提示词

\`\`\`text
用 novel-studio 帮我判断当前这一步该走哪个小说技能。
\`\`\`

## 卸载

运行 \`python3 uninstall_codex_plugin.py\`。

如果你明确想把整个本地 marketplace 入口也移除，再运行：

\`\`\`bash
python3 uninstall_codex_plugin.py --remove-marketplace
\`\`\`
MD

(
  cd "$(dirname "${OUT_DIR}")"
  zip -qr "${ZIP_PATH}" "$(basename "${OUT_DIR}")"
)

printf 'Bundle directory: %s\n' "${OUT_DIR}"
printf 'Zip archive: %s\n' "${ZIP_PATH}"
