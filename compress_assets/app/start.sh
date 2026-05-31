#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is not installed. Please install Node.js first."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is not installed. Please install Python 3 first."
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg is not installed. Install it first, then run ./start.sh again."
  echo "Debian/Ubuntu: sudo apt-get update && sudo apt-get install -y ffmpeg"
  exit 1
fi

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
echo "Installing backend dependencies..."
python -m pip install --upgrade pip >/dev/null
python -m pip install -r requirements.txt >/dev/null

cleanup() {
  if [ -n "${BACKEND_PID:-}" ] && kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    echo ""
    echo "Stopping backend..."
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

echo "Starting backend API on http://localhost:8000 ..."
python -m uvicorn backend_api:app --host 0.0.0.0 --port 8000 --reload >/tmp/compress-assets-backend.log 2>&1 &
BACKEND_PID=$!

echo "Waiting for backend to become healthy..."
for _ in {1..30}; do
  if curl -fsS "http://localhost:8000/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! curl -fsS "http://localhost:8000/api/health" >/dev/null 2>&1; then
  echo "Backend failed to start. Recent logs:"
  tail -n 30 /tmp/compress-assets-backend.log || true
  exit 1
fi

echo "Starting frontend UI on http://localhost:5173 ..."
VITE_API_BASE_URL="http://localhost:8000" npm run dev
