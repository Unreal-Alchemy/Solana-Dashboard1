import streamlit as st
import requests
import pandas as pd
import yfinance as yf

# Auto-refresh every 15 seconds
st_autorefresh = st.experimental_rerun if st.experimental_get_query_params() else lambda: None
st_autorefresh()

st.set_page_config(page_title="Solana Trading Dashboard", layout="wide")
st.title("📊 Real-Time Solana (SOL) Dashboard")

def get_sol_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    return requests.get(url).json()["solana"]["usd"]

def get_tps():
    try:
        url = "https://api.validators.app/api/v1/tps/history?network=mainnet"
        data = requests.get(url).json()
        return round(data["data"][-1]["value"], 2)
    except:
        return "N/A"

def get_wallet_count():
    try:
        url = "https://api.helius.xyz/v0/addresses/active?api-key=YOUR_API_KEY"
        return requests.get(url).json().get("numActiveAddresses", "N/A")
    except:
        return "N/A"

def get_fee_estimate():
    try:
        url = "https://api.solana.fm/v0/network/fees"
        return requests.get(url).json()["data"]["totalFees"]
    except:
        return "N/A"

# Get data
sol_price = get_sol_price()
tps = get_tps()
wallets = get_wallet_count()
fees = get_fee_estimate()

# Display
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 SOL Price (USD)", f"${sol_price}")
c2.metric("⚡ TPS", f"{tps}")
c3.metric("👛 Active Wallets (24h)", f"{wallets}")
c4.metric("💸 24h Fees (SOL)", f"{fees}")
