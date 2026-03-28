#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENVP="$PROJECT_DIR/.venv"
BIN_DIR="${HOME}/.local/bin"
LAUNCHER="${BIN_DIR}/lopam"

python3 -m venv "$VENVP"
"$VENVP/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

mkdir -p "$BIN_DIR"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$PROJECT_DIR"
. "\$PROJECT_DIR/.venv/bin/activate"
exec python "\$PROJECT_DIR/main.py" "\$@"
EOF
chmod +x "$LAUNCHER"

echo "Installed. Ensure ${BIN_DIR} is in your PATH. Try: lopam --help"