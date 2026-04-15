#!/bin/bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs"
PID_DIR="${PROJECT_ROOT}/.pids"

mkdir -p "${LOG_DIR}" "${PID_DIR}"

cleanup() {
  echo ""
  echo "Stopping all dev services..."
  for pid_file in "${PID_DIR}"/*.pid; do
    if [ -f "${pid_file}" ]; then
      name=$(basename "${pid_file}" .pid)
      pid=$(cat "${pid_file}")
      if kill -0 "${pid}" 2>/dev/null; then
        echo "  Stopping ${name} (PID ${pid})..."
        kill "${pid}" 2>/dev/null || true
      fi
      rm -f "${pid_file}"
    fi
  done
  echo "All services stopped."
  exit 0
}
trap cleanup SIGINT SIGTERM

log() {
  echo -e "[\033[1;36m${1}\033[0m] ${2}"
}

# Start backend (Docker Compose)
log "BACKEND" "Starting infrastructure and backend..."
cd "${PROJECT_ROOT}"
mise run docker:dev > "${LOG_DIR}/backend.log" 2>&1 &
BACKEND_PID=$!
echo ${BACKEND_PID} > "${PID_DIR}/backend.pid"
log "BACKEND" "Started (PID ${BACKEND_PID})"

# Start frontend with Vite
log "FRONTEND" "Starting frontend with Vite..."
cd "${PROJECT_ROOT}/frontend"
npm run dev > "${LOG_DIR}/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo ${FRONTEND_PID} > "${PID_DIR}/frontend.pid"
log "FRONTEND" "Running at http://localhost:3000 (PID ${FRONTEND_PID})"

echo ""
echo "========================================"
echo " Dev environment running!"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  Docker Compose (see logs/)"
echo ""
echo " Logs: logs/*.log"
echo " PIDs:  .pids/*.pid"
echo ""
echo " Press Ctrl+C to stop all services."
echo "========================================"
echo ""

# Wait for all background processes
wait