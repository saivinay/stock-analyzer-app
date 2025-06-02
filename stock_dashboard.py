import streamlit as st
import requests
import pandas as pd

# Replace with your actual FMP API key
API_KEY = "eLZVIiG9DSAFlfqQ48Q7vxcfIDF3lFv2"

# Default list of stock tickers
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "BRK.B", "UNH", "JNJ"]

# Function to safely format values
def safe_format(val, fmt):
    try:
        return fmt.format(val)
    except:
        return "N/A"

# Function to score stocks based on financial metrics
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

# Function to fetch stock data from FMP
def fetch_stock_data(symbol):
    # Normalize symbol for FMP (replace '.' with '-')
    symbol = symbol.replace('.', '-')
    base_url = "https://financialmodelingprep.com/api/v3"
    try:
        # Fetch quote data
        quote_resp = requests.get(f"{base_url}/quote/{symbol}?apikey={API_KEY}")
        quote_data = quote_resp.json()
        if not quote_data:
            raise ValueError("No quote data")
        quote = quote_data[0]

        # Fetch key metrics TTM
        key_metrics_resp = requests.get(f"{base_url}/key-metrics-ttm/{symbol}?apikey={API_KEY}")
        key_metrics_data = key_metrics_resp.json()
        if not key_metrics_data:
            raise ValueError("No key metrics data")
        key_metrics = key_metrics_data[0]

        # Fetch ratios TTM
        ratios_resp = requests.get(f"{base_url}/ratios-ttm/{symbol}?apikey={API_KEY}")
        ratios_data = ratios_resp.json()
        if not ratios_data:
            raise ValueError("No ratios data")
        ratios = ratios_data[0]

        return {
            "Ticker": symbol.replace('-', '.'),
            "Price": quote.get("price"),
            "Market Cap": quote.get("marketCap"),
            "PE Ratio": key_metrics.get("peRatio"),
            "EPS": key_metrics.get("eps"),
            "P/B Ratio": key_metrics.get("pbRatio"),
            "Dividend Yield": (key_metrics.get("dividendYield") or 0) * 100,
            "ROE": (ratios.get("returnOnEquity") or 0) * 100,
            "Debt to Equity": ratios.get("debtEquityRatio"),
            "P/S Ratio": key_metrics.get("priceToSalesRatio"),
            "EV/EBITDA": key_metrics.get("enterpriseValueOverEBITDA"),
            "Operating Margin": (ratios.get("operatingProfitMargin") or 0) * 100,
            "FCF Margin": (ratios.get("freeCashFlowMargin") or 0) * 100,
        }
    except Exception as e:
        st.warning(f"⚠️ Error fetching {symbol}: {e}")
        return None

# Streamlit App
st.title("📈 Stock Fundamentals Analyzer")

# Input for stock tickers
tickers_input = st.text_input("Enter comma-separated stock tickers:", ",".join(DEFAULT_TICKERS))
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

with st.spinner("Fetching stock data..."):
    data = [fetch_stock_data(t) for t in tickers]
    data = [d for d in data if d]  # Remove None entries

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
