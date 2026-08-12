#!/bin/bash

# =========================================================
# STREAMLIT WATCHDOG
# =========================================================

DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"

START_SCRIPT="$DEPLOY_DIR/start_streamlit.sh"

LOG="$DEPLOY_DIR/streamlit_watchdog.log"

# =========================================================
# LOAD CONFIGURATION
# =========================================================

APP_FILE=$(grep '^APP_FILE=' "$START_SCRIPT" | cut -d'"' -f2)
PORT=$(grep '^PORT=' "$START_SCRIPT" | cut -d'"' -f2)

# =========================================================
# CEK STREAMLIT
# =========================================================

if pgrep -u "$(whoami)" -f "streamlit run $APP_FILE.*--server.port=$PORT" > /dev/null
then
    exit 0
fi

# =========================================================
# STREAMLIT TIDAK BERJALAN
# =========================================================

echo "$(date '+%Y-%m-%d %H:%M:%S') - Streamlit tidak berjalan. Menjalankan kembali..." >> "$LOG"

# =========================================================
# START
# =========================================================

nohup "$START_SCRIPT" >> "$DEPLOY_DIR/streamlit.log" 2>&1 &

echo "$(date '+%Y-%m-%d %H:%M:%S') - $START_SCRIPT dijalankan." >> "$LOG"