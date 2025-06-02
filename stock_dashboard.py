

import streamlit as st
import requests
import pandas as pd

# 👉 Replace with your actual FMP API key
API_KEY = "eLZVIiG9DSAFlfqQ48Q7vxcfIDF3lFv2"

# Top stock tickers (customizable)
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "BRK.B", "UNH", "JNJ"]

# Safe value formatter
def safe_format(val, fmt):
    try:
        return fmt.format(val)
    except:
        return "N/A"

# Scoring logic for stocks
def score_stock(row):
    score = 0
    try:
        if 0 < float(row['PE Ratio']) < 20: score += 1
    except: pass
    try:
        if 0 < float(row['P/B Ratio']) < 3: score += 1
    except: pass
    try:
        if float(row['Dividend Yield']) > 0: score += 1
    except: pass
    try:
        if float(row['ROE']) > 10: score += 1
    except: pass
    try:
        if float(row['Debt to Equity']) < 1: score += 1
    except: pass
    try:
        if float(row['EPS']) > 0: score += 1
    except: pass
    try:
        if float(row['Operating Margin']) > 0: score += 1
    except: pass
    try:
        if float(row['FCF Margin']) > 0: score += 1
    except: pass
    return score

# Fetch financials for one stock
def fetch_stock_data(symbol):
    base = "https://financialmodelingprep.com/api/v3"
    try:
        quote = requests.get(f"{base}/quote/{symbol}?apikey={API_KEY}").json()[0]
        profile = requests.get(f"{base}/profile/{symbol}?apikey={API_KEY}").json()[0]
        key_metrics = requests.get(f"{base}/key-metrics-ttm/{symbol}?apikey={API_KEY}").json()[0]
        ratios = requests.get(f"{base}/ratios-ttm/{symbol}?apikey={API_KEY}").json()[0]

        return {
            "Ticker": symbol,
            "Price": quote.get("price"),
            "Market Cap": quote.get("marketCap"),
            "PE Ratio": key_metrics.get("peRatio"),
            "EPS": key_metrics.get("eps"),
            "P/B Ratio": key_metrics.get("pbRatio"),
            "Dividend Yield": key_metrics.get("dividendYield") * 100 if key_metrics.get("dividendYield") else None,
            "ROE": ratios.get("returnOnEquity") * 100 if ratios.get("returnOnEquity") else None,
            "Debt to Equity": ratios.get("debtEquityRatio"),
            "P/S Ratio": key_metrics.get("priceToSalesRatio"),
            "EV/EBITDA": key_metrics.get("enterpriseValueOverEBITDA"),
            "Operating Margin": ratios.get("operatingProfitMargin") * 100 if ratios.get("operatingProfitMargin") else None,
            "FCF Margin": ratios.get("freeCashFlowMargin") * 100 if ratios.get("freeCashFlowMargin") else None,
        }
    except Exception as e:
        st.warning(f"⚠️ Error fetching {symbol}: {e}")
        return None

# Streamlit App
st.title("📈 Stock Fundamentals Analyzer")

tickers = st.text_input("Enter comma-separated stock tickers:", ",".join(DEFAULT_TICKERS))
tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]

with st.spinner("Fetching stock data..."):
    data = [fetch_stock_data(t) for t in tickers]
    data = [d for d in data if d]  # remove failed entries

if not data:
    st.error("❌ No stock data could be loaded. Please check your internet connection or API key.")
    st.stop()

df = pd.DataFrame(data)
df["Score"] = df.apply(score_stock, axis=1)
df = df.sort_values(by="Score", ascending=False)

# Format numeric fields safely
df["Dividend Yield"] = df["Dividend Yield"].apply(lambda x: safe_format(x, "{:.2f}%"))
df["ROE"] = df["ROE"].apply(lambda x: safe_format(x, "{:.2f}%"))
df["Debt to Equity"] = df["Debt to Equity"].apply(lambda x: safe_format(x, "{:.2f}"))
df["PE Ratio"] = df["PE Ratio"].apply(lambda x: safe_format(x, "{:.2f}"))
df["P/B Ratio"] = df["P/B Ratio"].apply(lambda x: safe_format(x, "{:.2f}"))
df["P/S Ratio"] = df["P/S Ratio"].apply(lambda x: safe_format(x, "{:.2f}"))
df["EV/EBITDA"] = df["EV/EBITDA"].apply(lambda x: safe_format(x, "{:.2f}"))
df["Operating Margin"] = df["Operating Margin"].apply(lambda x: safe_format(x, "{:.2f}%"))
df["FCF Margin"] = df["FCF Margin"].apply(lambda x: safe_format(x, "{:.2f}%"))
df["Market Cap"] = df["Market Cap"].apply(lambda x: safe_format(x, "{:,.0f}"))
df["Price"] = df["Price"].apply(lambda x: safe_format(x, "${:.2f}"))
df["EPS"] = df["EPS"].apply(lambda x: safe_format(x, "{:.2f}"))

st.success(f"✅ Analyzed {len(df)} stocks.")
st.dataframe(df, use_container_width=True)

# Download button
st.download_button("📥 Download CSV", df.to_csv(index=False), "stock_analysis.csv")
