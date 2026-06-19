# M5 Bot — Tek Model Paket (vedat)

Bu paket **sadece M5 botunu** çalıştırır. Kripto trend-takip botu + Binance veri çekme +
backtest + canlı paper-trading + dashboard arayüzü içerir. **Pushlandığında yalnız M5 koşar.**

## İçindekiler
```
vedat/
├── crypto_portfolio_test.py   # Ana motor: Binance veri çekme + backtest + M5 stratejisi
├── strategy/                  # Strateji modülleri (trend-following, regime, coin seçimi, WFO)
├── indicators/                # Teknik indikatörler (EMA, ADX, RSI, ATR...)
├── risk/                      # Risk yönetimi (korelasyon, pozisyon boyutu)
├── live/
│   ├── live_engine.py         # Canlı motor (M5'i çalıştırır)
│   └── live_runner.py         # SADECE M5 tick atan döngü
├── dashboard/
│   ├── app.py                 # M5 canlı dashboard (Streamlit)
│   └── state.py               # SQLite state DB
├── config.yaml                # Ayarlar
├── requirements.txt           # Bağımlılıklar
├── start.sh                   # AWS/lokal başlatma
└── README.md
```

## Veri Kaynağı
- **Binance** borsasından `ccxt` ile gerçek geçmiş + canlı OHLCV verisi.
- LEO için OKX (Binance'te yok). Disk cache `.ohlcv_cache/` ile tekrar çekim önlenir.

## Kurulum & Çalıştırma

### Hızlı (AWS / Ubuntu)
```bash
cd vedat
chmod +x start.sh
./start.sh          # venv kurar, botu + dashboard'ı screen'de başlatır
```
- Bot: her 15 dakikada bir tick (`screen -r m5live`)
- Dashboard: `http://<sunucu-ip>:8501`

### Manuel
```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# Canlı bot (paper, $1000)
venv/bin/python live/live_runner.py --fresh --capital 1000   # sıfırdan başlat
venv/bin/python live/live_runner.py --loop 900               # her 15 dk tick

# Dashboard
venv/bin/streamlit run dashboard/app.py

# Backtest (M5)
venv/bin/python crypto_portfolio_test.py --m5 --universe --start 2026-01-01 --end 2026-05-15
```

## M5 Nedir?
Agresif adaptif trend-takip modeli (15m, spot):
- **Sinyal:** EMA50/200 + ADX + RSI + ATR + Volume + BTC rejim filtresi
- **Boyut:** ATR-yüzdelik (oynaklığa göre risk-parite)
- **Risk:** ATR-stop (2.5×) + trailing + circuit breaker + 3 gün cooldown
- **Coin:** 25+ coinlik evrenden dinamik en uygun ~15

## Notlar
- Paper-trade (sanal sermaye) — gerçek emir göndermez.
- `--fresh` state'i sıfırlar; dikkatli kullan.
- Tek model: bu pakette M4/M6/M7/M9/ORTAK YOK, sadece M5.
