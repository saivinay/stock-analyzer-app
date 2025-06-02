import streamlit as st
import yfinance as yf
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Top Stocks Analyzer", layout="wide")

# --- Custom stock scoring function ---
def score_stock(row):
    score = 0
    try:
        if row['PE Ratio'] > 0 and row['PE Ratio'] < 20:
            score += 1
        if row['P/B Ratio'] > 0 and row['P/B Ratio'] < 3:
            score += 1
        if row['Dividend Yield'] > 0:
            score += 1
        if row['ROE'] > 10:
            score += 1
        if row['Debt to Equity'] < 1:
            score += 1
        if row['EPS'] > 0:
            score += 1
        if row['Operating Margin'] > 0:
            score += 1
        if row['FCF'] > 0:
            score += 1
    except:
        pass
    return score

# --- Simulate top 10 tickers (can be replaced with live logic) ---
def get_top_10_tickers():
    return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'BRK-B', 'UNH', 'JNJ']

# --- Pull metrics for a single ticker ---
def fetch_metrics(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            'Ticker': ticker,
            'PE Ratio': info.get('trailingPE', None),
            'EPS': info.get('trailingEps', None),
            'P/B Ratio': info.get('priceToBook', None),
            'Dividend Yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'ROE': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
            'Debt to Equity': info.get('debtToEquity', None),
            'Market Cap': info.get('marketCap', None),
            'Price/Sales': info.get('priceToSalesTrailing12Months', None),
            'FCF': info.get('freeCashflow', None),
            'EV/EBITDA': info.get('enterpriseToEbitda', None),
            'Operating Margin': info.get('operatingMargins', 0) * 100 if info.get('operatingMargins') else 0
        }
    except Exception as e:
        st.warning(f"Error fetching {ticker}: {e}")
        return None

# --- Main logic ---
st.title("📈 Top 10 Stock Analyzer")

tickers = get_top_10_tickers()
st.subheader("Analyzing Top Tickers:")
st.write(tickers)

metrics = []
for ticker in tickers:
    data = fetch_metrics(ticker)
    if data:
        metrics.append(data)

# Convert to DataFrame
df = pd.DataFrame(metrics)

# Handle empty DataFrame
if df.empty or df.isnull().all(axis=1).all():
    st.error("❌ No stock data could be loaded. Please check your internet connection or data source.")
    st.stop()

# Apply scoring
df['Score'] = df.apply(score_stock, axis=1)

# Sort by score
df = df.sort_values(by='Score', ascending=False)

# Show results
st.success("✅ Top Stocks Based on Fundamentals:")
st.dataframe(df.style.format({
    'Dividend Yield': '{:.2f}%',
    'ROE': '{:.2f}%',
    'Operating Margin': '{:.2f}%',
    'PE Ratio': '{:.2f}',
    'P/B Ratio': '{:.2f}',
    'Price/Sales': '{:.2f}',
    'EV/EBITDA': '{:.2f}',
    'EPS': '{:.2f}',
    'Debt to Equity': '{:.2f}',
}))

# Optional CSV export
st.download_button("📥 Download Results as CSV", data=df.to_csv(index=False), file_name="top_stocks.csv")
