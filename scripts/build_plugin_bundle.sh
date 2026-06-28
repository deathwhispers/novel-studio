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
    "displayName": "Novel Skills Local"
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
# Novel Skills Local Plugin Bundle

Build timestamp: ${timestamp}
Source commit: ${git_sha}

## Install

1. Unzip this bundle.
2. Run \`python3 install_codex_plugin.py\`.
3. Restart Codex if it is already open.
4. Start a new thread before testing.

## What The Installer Does

- Registers this directory as a local Codex marketplace with \`codex plugin marketplace add\`.
- Copies the plugin into \`~/.codex/plugins/cache/novel-local/novel-skills/<version>\`.
- Ensures \`[features] plugins = true\` is set in \`~/.codex/config.toml\`.
- Enables \`novel-skills@novel-local\` in \`~/.codex/config.toml\`.

## Test Prompt

\`\`\`text
Use novel-studio to route my current fiction-writing task.
\`\`\`

## Uninstall

Run \`python3 uninstall_codex_plugin.py\`.
MD

(
  cd "$(dirname "${OUT_DIR}")"
  zip -qr "${ZIP_PATH}" "$(basename "${OUT_DIR}")"
)

printf 'Bundle directory: %s\n' "${OUT_DIR}"
printf 'Zip archive: %s\n' "${ZIP_PATH}"
