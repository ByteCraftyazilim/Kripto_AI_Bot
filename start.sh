#!/bin/bash
# M5 Bot — başlatma scripti (AWS / lokal)
# Botu (15 dk döngü) ve dashboard'ı screen oturumlarında başlatır.
cd "$(dirname "$0")"

# venv yoksa oluştur + bağımlılıkları kur
if [ ! -d venv ]; then
    echo "📦 venv oluşturuluyor + bağımlılıklar kuruluyor..."
    python3 -m venv venv
    venv/bin/pip install -q --upgrade pip
    venv/bin/pip install -q -r requirements.txt
fi

mkdir -p logs live/state

# Eski oturumları kapat
screen -S m5live -X quit 2>/dev/null
screen -S m5dash -X quit 2>/dev/null
sleep 1

# Bot döngüsü (her 15 dk = 900s)
screen -dmS m5live bash -c "cd $(pwd) && venv/bin/python -u live/live_runner.py --loop 900 >> logs/m5_live.log 2>&1"

# Dashboard (port 8501)
screen -dmS m5dash bash -c "cd $(pwd) && venv/bin/streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 >> logs/m5_dash.log 2>&1"

sleep 2
echo "✅ M5 Bot başlatıldı:"
echo "   • Bot döngüsü:  screen -r m5live   (log: logs/m5_live.log)"
echo "   • Dashboard:    http://<sunucu-ip>:8501   (log: logs/m5_dash.log)"
echo ""
screen -ls | grep -E "m5live|m5dash"
