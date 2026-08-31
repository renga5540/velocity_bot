import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@velocity_newsignal")

def get_signal(symbol):
    try:
        data = yf.download(symbol, period="1d", interval="5m", progress=False)
        if data.empty or len(data) < 20:
            return None
        
        close = data['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        
        # Simple velocity logic
        price = float(close.iloc[-1])
        prev = float(close.iloc[-2])
        ema9 = float(close.ewm(span=9).mean().iloc[-1])
        ema21 = float(close.ewm(span=21).mean().iloc[-1])
        
        if price > ema9 > ema21 and price > prev:
            return f"BUY {symbol} | ENTRY {price:.2f} | SL {price*0.998:.2f} | T1 {price*1.002:.2f} | T2 {price*1.005:.2f}"
        elif price < ema9 < ema21 and price < prev:
            return f"SELL {symbol} | ENTRY {price:.2f} | SL {price*1.002:.2f} | T1 {price*0.998:.2f} | T2 {price*0.995:.2f}"
        return None
    except Exception as e:
        print(f"Error {symbol}: {e}")
        return None

def send_telegram(text):
    if not TOKEN:
        print("❌ TOKEN MISSING! Secret add pannala!")
        return False
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"Telegram Response: {r.text}")
        return r.ok
    except Exception as e:
        print(f"Telegram Error: {e}")
        return False

# --- MAIN ---
symbols = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "XAUUSD=X", "BTC-USD", "ETH-USD"]
signals = []

print(f"--- Velocity Bot {datetime.now()} ---")
for sym in symbols:
    s = get_signal(sym)
    if s:
        print(s)
        signals.append(s)

if signals:
    msg = f"🚀 <b>VELOCITY SIGNALS {datetime.now().strftime('%H:%M')}</b>\n\n" + "\n\n".join(signals) + "\n\n⚠️ Not financial advice"
    send_telegram(msg)
else:
    print("No signals now")
    send_telegram(f"✅ Bot Live Check {datetime.now().strftime('%H:%M')} - No strong signals now")
