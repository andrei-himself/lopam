#!/usr/bin/env bash
set -euo pipefail
BIN_DIR="${HOME}/.local/bin"
LAUNCHER="${BIN_DIR}/lopam"

# Discover vaults path by reading config if present
CFG="${HOME}/.config/lopam/config.json"
if [ -f "$CFG" ]; then
  VAULTS_PATH=$(python - <<'PY'
import json, os, sys
cfg = json.load(open(os.path.expanduser("~/.config/lopam/config.json")))
print(cfg.get("vaults_dir","~/.local/share/lopam/vaults"))
PY
)
else
  VAULTS_PATH="~/.local/share/lopam/vaults"
fi

rm -f "$LAUNCHER"
echo "Program uninstalled. Your vaults are in ${VAULTS_PATH}."