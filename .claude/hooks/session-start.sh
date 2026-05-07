#!/bin/bash
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

# Install Python dependencies
echo "[hook] Installing Python dependencies..."
pip3 install -q telethon python-dotenv openai-whisper pdfplumber python-docx openpyxl "numpy<2" 2>&1 | tail -5

# Restore .env if env vars are available but .env is missing
if [ ! -f "$PROJECT_DIR/.env" ] && [ -n "${TELEGRAM_API_ID:-}" ]; then
  echo "[hook] Restoring .env from environment variables..."
  cat > "$PROJECT_DIR/.env" << EOF
TELEGRAM_API_ID=${TELEGRAM_API_ID}
TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
TELEGRAM_PHONE=${TELEGRAM_PHONE:-}
SESSION_NAME=${SESSION_NAME:-ruslan_bsag}
EOF
fi

# Restore Telegram session file from base64 env var
SESSION_NAME_VAL="${SESSION_NAME:-ruslan_bsag}"
SESSION_FILE="$PROJECT_DIR/${SESSION_NAME_VAL}.session"

if [ ! -f "$SESSION_FILE" ] && [ -n "${TELEGRAM_SESSION_B64:-}" ]; then
  echo "[hook] Restoring Telegram session file from TELEGRAM_SESSION_B64..."
  echo "${TELEGRAM_SESSION_B64}" | base64 -d > "$SESSION_FILE"
  echo "[hook] Session file restored: $SESSION_FILE"
fi

if [ -f "$SESSION_FILE" ]; then
  echo "[hook] Telegram session file present: ${SESSION_NAME_VAL}.session"
else
  echo "[hook] WARNING: No session file found. Run auth.py to authenticate first."
fi

echo "[hook] Done."
