#!/bin/bash

# =========================================================
# STREAMLIT WATCHDOG
# =========================================================

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
START_SCRIPT="$APP_DIR/start_streamlit.sh"
LOG="$APP_DIR/streamlit_watchdog.log"

# =========================================================
# CEK APAKAH STREAMLIT APLIKASI INI MASIH BERJALAN
# =========================================================

if pgrep -u "$(whoami)" -f "streamlit run landscape.py --server.address=127.0.0.1 --server.port=8501" > /dev/null
then
    exit 0
fi

# =========================================================
# STREAMLIT TIDAK BERJALAN
# =========================================================

echo "$(date '+%Y-%m-%d %H:%M:%S') - Streamlit tidak berjalan. Menjalankan kembali..." >> "$LOG"

# =========================================================
# JALANKAN KEMBALI
# =========================================================

nohup "$START_SCRIPT" >> "$APP_DIR/streamlit.log" 2>&1 &

echo "$(date '+%Y-%m-%d %H:%M:%S') - $START_SCRIPT dijalankan." >> "$LOG"