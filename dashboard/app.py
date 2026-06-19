"""
M5 Bot — Canlı Dashboard (Streamlit)
=====================================
SADECE M5 botunu gösterir. live/state/m5_state.json dosyasını okur.

Çalıştırma:
    streamlit run dashboard/app.py
    # veya AWS'de:  streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
"""
from __future__ import annotations
import json
import math
import statistics as st
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import streamlit as stl

_ROOT = Path(__file__).resolve().parent.parent
M5_STATE = _ROOT / "live" / "state" / "m5_state.json"

stl.set_page_config(page_title="M5 Bot — Canlı", page_icon="🟣", layout="wide")


def load_state() -> dict | None:
    if not M5_STATE.exists():
        return None
    with open(M5_STATE, encoding="utf-8") as f:
        return json.load(f)


def sharpe_omega(eq_hist: list) -> tuple[float | None, float | None]:
    """equity_history [[tarih, equity], ...] → günlük Sharpe + Omega (√365)."""
    if len(eq_hist) < 3:
        return None, None
    vals = [float(v) for _, v in eq_hist]
    rets = [vals[i] / vals[i - 1] - 1 for i in range(1, len(vals))]
    if len(rets) < 2 or st.pstdev(rets) == 0:
        return None, None
    sharpe = st.mean(rets) / st.stdev(rets) * math.sqrt(365)
    g = sum(r for r in rets if r > 0)
    l = abs(sum(r for r in rets if r < 0))
    omega = (g / l) if l > 0 else float("inf")
    return sharpe, omega


# ── Başlık ──────────────────────────────────────────────────────────────────
stl.title("🟣 M5 Bot — Canlı Paper Trading")
stl.caption("Agresif Adaptif Trend-Takip Modeli · 15m · Binance · 25+ coin")

state = load_state()
if state is None:
    stl.warning("Henüz M5 state'i yok. Bot en az bir tick attıktan sonra burada görünecek.\n\n"
                "Botu başlat: `python live/live_runner.py --loop 900`")
    stl.stop()

# ── Üst metrikler ───────────────────────────────────────────────────────────
init_cap = state.get("initial_capital", 1000.0)
balance = state.get("final_balance", state.get("balance", init_cap))
total_pnl = state.get("total_pnl", 0.0)
ret_pct = state.get("total_pnl_pct", 100 * (balance / init_cap - 1) if init_cap else 0)
wr = state.get("win_rate", 0.0)
n_trades = state.get("total_trades", len(state.get("closed_trades", [])))
max_dd = state.get("max_drawdown_pct", 0.0)
open_pos = state.get("open_positions", [])
sharpe, omega = sharpe_omega(state.get("equity_history", []))

c1, c2, c3, c4 = stl.columns(4)
c1.metric("💰 Bakiye", f"${balance:,.2f}", f"{ret_pct:+.2f}%")
c2.metric("📊 Toplam PnL", f"${total_pnl:+,.2f}")
c3.metric("🎯 Kazanma Oranı", f"%{wr:.1f}", f"{n_trades} işlem")
c4.metric("📉 Max Düşüş", f"%{max_dd:.1f}")

c5, c6, c7 = stl.columns(3)
c5.metric("📐 Sharpe", f"{sharpe:.2f}" if sharpe is not None else "— (≥5 gün)")
c6.metric("Ω Omega", f"{omega:.2f}" if omega is not None else "—")
c7.metric("🔓 Açık Pozisyon", str(len(open_pos)))

stl.divider()

# ── Equity grafiği ──────────────────────────────────────────────────────────
eq_hist = state.get("equity_history", [])
if len(eq_hist) >= 2:
    stl.subheader("📈 Equity Eğrisi")
    df_eq = pd.DataFrame(eq_hist, columns=["tarih", "equity"]).set_index("tarih")
    stl.line_chart(df_eq, height=260)

# ── Açık pozisyonlar ────────────────────────────────────────────────────────
stl.subheader("🔓 Açık Pozisyonlar")
if open_pos:
    rows = []
    for p in open_pos:
        rows.append({
            "Coin": p.get("symbol"),
            "Yön": "SHORT" if p.get("is_short") else "LONG",
            "Giriş": round(p.get("entry_price", 0), 6),
            "Boyut": round(p.get("size", 0), 4),
            "Stop": round(p.get("stop", 0), 6) if p.get("stop") else "—",
        })
    stl.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    stl.info("Şu an açık pozisyon yok (nakitte).")

# ── Kapalı işlemler ─────────────────────────────────────────────────────────
stl.subheader("📋 Son Kapalı İşlemler")
closed = state.get("closed_trades", [])
if closed:
    rows = []
    for t in closed[-30:][::-1]:  # son 30, ters
        rows.append({
            "Coin": t.get("symbol"),
            "Yön": "SHORT" if t.get("is_short") else "LONG",
            "Giriş": round(t.get("entry_price", 0), 6),
            "Çıkış": round(t.get("exit_price", 0), 6),
            "PnL $": round(t.get("pnl", 0), 2),
            "Sebep": t.get("exit_reason", ""),
            "Çıkış Tarihi": str(t.get("exit_date", ""))[:16],
        })
    stl.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    stl.caption(f"Toplam {len(closed)} kapalı işlem · son 30 gösteriliyor")
else:
    stl.info("Henüz kapalı işlem yok.")

# ── Alt bilgi ───────────────────────────────────────────────────────────────
stl.divider()
upd = state.get("updated_at", "—")
created = state.get("created_at", "—")
stl.caption(f"Başlangıç: {str(created)[:16]} · Son güncelleme: {str(upd)[:16]} · "
            f"Başlangıç sermaye: ${init_cap:,.0f}")
if stl.button("🔄 Yenile"):
    stl.rerun()
