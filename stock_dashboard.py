import streamlit as st
import requests
import pandas as pd

FMP_API_KEY = "eLZVIiG9DSAFlfqQ48Q7vxcfIDF3lFv2"  # 🔁 Replace with your actual FMP API key
BASE_URL = "https://financialmodelingprep.com/api/v3"

st.set_page_config(page_title="Top Stocks Analyzer (FMP)", layout="wide")
st.title("📊 Top Stocks Analyzer (via Financial Modeling Prep API)")

def get_top_10_stocks():
    # Example: get largest market cap stocks (you can use other endpoints too)
    url = f"{BASE_URL}/stock-screener?limit=10&exchange=NASDAQ&apikey={FMP_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return [stock['symbol'] for stock in response.json()]
    return []

def fetch_metrics(ticker):
    try:
        profile_url = f"{BASE_URL}/profile/{ticker}?apikey={FMP_API_KEY}"
        ratios_url = f"{BASE_URL}/ratios-ttm/{ticker}?apikey={FMP_API_KEY}"

        profile_resp = requests.get(profile_url)
        ratios_resp = requests.get(ratios_url)

        if profile_resp.status_code != 200 or ratios_resp.status_code != 200:
            raise Exception("API call failed")

        profile = profile_resp.json()[0]
        ratios = ratios_resp.json()[0]

        return {
            'Ticker': ticker,
            'Company': profile.get('companyName'),
            'Market Cap': profile.get('mktCap'),
            'PE Ratio': ratios.get('peRatioTTM'),
            'EPS': profile.get('eps'),
            'P/B Ratio': ratios.get('priceToBookRatioTTM'),
            'Dividend Yield': ratios.get('dividendYieldTTM') * 100 if ratios.get('dividendYieldTTM') else 0,
            'ROE': ratios.get('returnOnEquityTTM') * 100 if ratios.get('returnOnEquityTTM') else 0,
            'Debt to Equity': ratios.get('debtEquityRatioTTM'),
            'Price/Sales': ratios.get('priceToSalesRatioTTM'),
            'Operating Margin': ratios.get('operatingProfitMarginTTM') * 100 if ratios.get('operatingProfitMarginTTM') else 0,
            'EV/EBITDA': ratios.get('evToEbitdaTTM'),
            'FCF Margin': ratios.get('freeCashFlowMarginTTM') * 100 if ratios.get('freeCashFlowMarginTTM') else 0
        }
    except Exception as e:
        st.warning(f"⚠️ Failed to fetch {ticker}: {e}")
        return None

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


# --- Main logic ---
tickers = get_top_10_stocks()
if not tickers:
    st.error("❌ Could not fetch top stocks. Check your FMP API key or quota.")
    st.stop()

st.subheader("Top 10 Stocks:")
st.write(tickers)

stock_data = []
for ticker in tickers:
    data = fetch_metrics(ticker)
    if data:
        stock_data.append(data)

df = pd.DataFrame(stock_data)
if df.empty:
    st.error("❌ No valid stock data retrieved.")
    st.stop()

df['Score'] = df.apply(score_stock, axis=1)
df = df.sort_values(by='Score', ascending=False)

st.success("✅ Top Stocks by Fundamentals:")
st.dataframe(df.style.format({
    'Dividend Yield': '{:.2f}%',
    'ROE': '{:.2f}%',
    'Operating Margin': '{:.2f}%',
    'FCF Margin': '{:.2f}%',
    'PE Ratio': '{:.2f}',
    'P/B Ratio': '{:.2f}',
    'Price/Sales': '{:.2f}',
    'EV/EBITDA': '{:.2f}',
    'EPS': '{:.2f}',
    'Debt to Equity': '{:.2f}',
    'Market Cap': '{:,.0f}',
}))

st.download_button("📥 Download CSV", data=df.to_csv(index=False), file_name="top_stocks_fmp.csv")
