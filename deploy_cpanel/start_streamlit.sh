#!/bin/bash

# =========================================================
# STREAMLIT DEPLOYMENT CONFIGURATION
# =========================================================

# Nama file aplikasi Streamlit
APP_FILE="versibaru.py"

# Port aplikasi
PORT="8501"

# =========================================================
# ENVIRONMENT
# =========================================================

# Batasi jumlah thread library numerik agar tidak membebani
# resource shared hosting / CloudLinux.
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# =========================================================
# PATH
# =========================================================

# Lokasi root aplikasi.
# Script berada di:
#   /home/.../APP/deploy/start_streamlit.sh
#
# sehingga parent dari folder deploy adalah root aplikasi.
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Ambil nama user Linux yang sedang menjalankan script.
CPANEL_USER="$(whoami)"

# Virtual environment Python cPanel.
VENV="/home/${CPANEL_USER}/virtualenv/$(basename "$APP_DIR")/3.11/bin"

# =========================================================
# START STREAMLIT
# =========================================================

cd "$APP_DIR" || exit 1

exec "$VENV/streamlit" run "$APP_FILE" \
    --server.address=127.0.0.1 \
    --server.port="$PORT"