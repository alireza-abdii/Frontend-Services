#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.services.yml"
CORE_URL="http://localhost:8200"

if ! command -v docker-compose >/dev/null 2>&1; then
  echo "docker-compose is required but not installed."
  exit 1
fi

usage() {
  cat <<'EOF'
Usage: ./run.sh <command>

Commands:
  up        Start all services
  down      Stop all services
  rebuild   Rebuild and restart all services
  logs      Follow logs for all services
  ps        Show running services
EOF
}

open_core_tab() {
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$CORE_URL" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then
    open "$CORE_URL" >/dev/null 2>&1 || true
  elif command -v sensible-browser >/dev/null 2>&1; then
    sensible-browser "$CORE_URL" >/dev/null 2>&1 || true
  else
    echo "Services are up. Open this URL manually: $CORE_URL"
  fi
}

cmd="${1:-}"
case "$cmd" in
  up)
    docker-compose -f "$COMPOSE_FILE" up -d
    open_core_tab
    ;;
  down)
    docker-compose -f "$COMPOSE_FILE" down
    ;;
  rebuild)
    docker-compose -f "$COMPOSE_FILE" up --build -d
    open_core_tab
    ;;
  logs)
    docker-compose -f "$COMPOSE_FILE" logs -f
    ;;
  ps)
    docker-compose -f "$COMPOSE_FILE" ps
    ;;
  *)
    usage
    exit 1
    ;;
esac
