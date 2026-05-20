#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=${DAYDREAM_ROOT:-$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)}
LOG_DIR=${DAYDREAM_LOG_DIR:-"$ROOT/logs"}
STAMP=$(date "+%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/daydream_$STAMP.log"

mkdir -p "$LOG_DIR"

run_daydream() {
  cd "$ROOT"
  export PYTHONPATH=${DAYDREAM_PYTHONPATH:-"$ROOT/src"}

  echo "daydream root: $ROOT"
  echo "started at: $(date)"
  python3 -m daydream doctor
  python3 -m daydream index

  if [ -z "${DAYDREAM_AGENT_CMD:-}" ]; then
    echo "DAYDREAM_AGENT_CMD is not set. Configure it to run your host agent with the daydream skill."
    return 2
  fi

  sh -c "$DAYDREAM_AGENT_CMD"
  python3 -m daydream inspect --run latest
  python3 -m daydream validate --run latest
}

if run_daydream >"$LOG_FILE" 2>&1; then
  echo "daydream cron run ok: $LOG_FILE"
else
  status=$?
  echo "daydream cron run failed with status $status: $LOG_FILE" >&2
  exit "$status"
fi
