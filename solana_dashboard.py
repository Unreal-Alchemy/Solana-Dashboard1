import streamlit as st
import requests
import pandas as pd
import yfinance as yf
import streamlit.components.v1 as components
from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import sun
from pytz import timezone as pytz_timezone

st.set_page_config(page_title="Solana Trading Dashboard", layout="wide")
st.title("📊 Solana (SOL) Dashboard")

# ------------------------- Data Fetching -------------------------

def get_sol_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    return requests.get(url).json()["solana"]["usd"]

def get_sol_dex_volume():
    url = "https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=1"
    data = requests.get(url).json()
    return round(sum(v[1] for v in data["total_volumes"]) / 1e9, 2)

def get_rsi(data, window=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ------------------------- Fetch & Process -------------------------

sol_price = get_sol_price()
volume_24h = get_sol_dex_volume()
sol_df = yf.download("SOL-USD", period="15d", interval="1h")
sol_df["RSI"] = get_rsi(sol_df["Close"])

# ------------------------- Display Metrics -------------------------

c1, c2, c3 = st.columns(3)
c1.metric("Current SOL Price", f"${sol_price}")
c2.metric("24h DEX Volume", f"${volume_24h}B")
c3.metric("RSI (14h)", f"{sol_df['RSI'].iloc[-1]:.2f}")

# ------------------------- RSI Signal -------------------------

st.subheader("📈 Trading Signal")
rsi = sol_df["RSI"].iloc[-1]
if rsi > 70:
    st.warning("RSI Overbought – Consider Profits")
elif rsi < 30:
    st.success("RSI Oversold – Entry Zone")
elif rsi >= 55:
    st.info("Momentum Building – Watch Breakout")
else:
    st.write("Neutral Zone")

# ------------------------- Strategy Zones -------------------------

st.markdown("---")
st.subheader("📌 Strategy Zones")
entry = sol_price * 0.98
tp = sol_price * 1.07
sl = sol_price * 0.96
st.code(f"Entry: ${entry:.2f}\nTake Profit: ${tp:.2f}\nStop Loss: ${sl:.2f}")

# ------------------------- Price Chart -------------------------

st.line_chart(sol_df["Close"])

# ------------------------- TradingView Embed -------------------------

st.subheader("📊 TradingView Live Chart")
tradingview_embed = """
<div class="tradingview-widget-container">
  <iframe src="https://s.tradingview.com/widgetembed/?symbol=BINANCE:SOLUSDT&interval=60&theme=dark&style=1&locale=en"
    width="100%" height="500" frameborder="0" allowtransparency="true" scrolling="no">
  </iframe>
</div>
"""
components.html(tradingview_embed, height=520)

# ------------------------- Rahu Kaal Toggle & Calculation -------------------------

show_rahu = st.toggle("🕉️ Show Rahu Kaal Timings")

if show_rahu:
    st.subheader("🕉️ Rahu Kaal Time Based on Your Location")

    # Ask for user location
    col1, col2 = st.columns(2)
    with col1:
        city = st.text_input("City", value="New Delhi")
    with col2:
        timezone_input = st.text_input("Timezone", value="Asia/Kolkata")

    # Setup location
    location = LocationInfo(city, "", timezone_input, 28.6139, 77.2090)

    # Real sunrise time
    s = sun(location.observer, date=datetime.now(), tzinfo=location.timezone)
    sunrise = s["sunrise"]

    def get_rahu_kaal_period(day_of_week, sunrise_time):
        rahu_kaal_offsets = {
            0: (7, 8.5),    # Monday
            1: (13, 14.5),  # Tuesday
            2: (10.5, 12),  # Wednesday
            3: (12, 13.5),  # Thursday
            4: (14.5, 16),  # Friday
            5: (8.5, 10),   # Saturday
            6: (9, 10.5)    # Sunday
        }
        start_offset, end_offset = rahu_kaal_offsets[day_of_week]
        start = sunrise_time + timedelta(hours=start_offset)
        end = sunrise_time + timedelta(hours=end_offset)
        return start, end

    weekday = datetime.now().weekday()
    rahu_start, rahu_end = get_rahu_kaal_period(weekday, sunrise)

    st.info(f"Today’s Rahu Kaal: {rahu_start.strftime('%I:%M %p')} - {rahu_end.strftime('%I:%M %p')}")

    # ✅ Timezone-aware current time
    now = datetime.now(pytz_timezone(timezone_input))
    if rahu_start <= now <= rahu_end:
        st.warning("⚠️ You are currently in Rahu Kaal — avoid new trades.")
        
