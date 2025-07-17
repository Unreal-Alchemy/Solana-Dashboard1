import streamlit as st
import requests
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Solana Trading Dashboard", layout="wide")
st.title("📊 Solana (SOL) Dashboard")

def get_sol_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    return requests.get(url).json()["solana"]["usd"]

def get_sol_dex_volume():
    url = "https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=1"
    data = requests.get(url).json()
    return round(sum(v[1] for v in data["total_volumes"]) / 1e9, 2)

def get_rsi(data, window=14):
    delta = data.diff()
    gain = delta.where(delta>0,0).rolling(window=window).mean()
    loss = -delta.where(delta<0,0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100/(1+rs))

sol_price = get_sol_price()
volume_24h = get_sol_dex_volume()
sol_df = yf.download("SOL-USD", period="15d", interval="1h")
sol_df["RSI"] = get_rsi(sol_df["Close"])

c1, c2, c3 = st.columns(3)
c1.metric("Current SOL Price", f"${sol_price}")
c2.metric("24h DEX Volume", f"${volume_24h}B")
c3.metric("RSI (14h)", f"{sol_df['RSI'].iloc[-1]:.2f}")

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

st.markdown("---")
st.subheader("📌 Strategy Zones")
entry = sol_price * 0.98
tp = sol_price * 1.07
sl = sol_price * 0.96

st.code(f"Entry: {entry:.2f}\nTake Profit: {tp:.2f}\nStop Loss: {sl:.2f}")
st.line_chart(sol_df["Close"])
