import yfinance as yf
import requests

TOKEN = "8781392368:AAEQ3K8axPmx1iZMXYWv-a_WhY3UjMIGr9M"
CHAT_ID = "1482959961"

SEGMENTS = {
    "INDIAN": ["^NSEI", "^NSEBANK"],
    "FOREX": ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "JPY=X"],
    "CRYPTO": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"],
    "GOLD": ["GC=F"]
}

def to_float(x):
    # Entha version a irunthalum work aagum
    try:
        return float(x)
    except:
        return float(x.values[0])

def send_telegram(text):
    url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
    for i in range(0, len(text), 4000):
        requests.post(url, data={"chat_id": CHAT_ID, "text": text[i:i+4000]})

def analyze(pair):
    try:
        df = yf.download(pair, period="6mo", auto_adjust=True, progress=False)
        if len(df) < 50:
            return None
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()

        close = to_float(df['Close'].iloc[-1])
        ema20 = to_float(df['EMA20'].iloc[-1])
        ema50 = to_float(df['EMA50'].iloc[-1])
        atr = to_float(df['ATR'].iloc[-1])
        if atr == 0:
            atr = close * 0.01

        if close > ema20 and ema20 > ema50:
            sig = "BUY"; sl = close-(atr*1.5); t1 = close+atr; t2 = close+(atr*2.5)
        elif close < ema20 and ema20 < ema50:
            sig = "SELL"; sl = close+(atr*1.5); t1 = close-atr; t2 = close-(atr*2.5)
        else:
            sig = "HOLD"; sl=0; t1=0; t2=0

        name = pair.replace("=X","").replace("-USD","/USD").replace("^NSEI","NIFTY").replace("^NSEBANK","BANKNIFTY").replace("GC=F","GOLD")

        if sig == "HOLD":
            return f"{sig} {name} @ {close:.2f} - Wait"
        else:
            return f"{sig} {name} | ENTRY {close:.2f} | SL {sl:.2f} | T1 {t1:.2f} | T2 {t2:.2f}"
    except Exception as e:
        print(f"Skip {pair}: {e}")
        return None

report = "VELOCITY AUTO SCAN - ALL MARKET\n------------------------------\n"
for seg_name, pairs in SEGMENTS.items():
    report += f"\n{seg_name}\n"
    for p in pairs:
        res = analyze(p)
        if res:
            report += res + "\n"

print(report)
send_telegram(report)
