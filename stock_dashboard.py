import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Top Stock Analyzer", layout="wide")

@st.cache_data(ttl=3600)
def get_top_10_stocks():
    url = "https://finance.yahoo.com/screener/predefined/most_actives"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', {'class': 'W(100%)'})

    tickers = []
    if table:
        rows = table.find_all('tr')[1:11]
        for row in rows:
            symbol = row.find('td').text.strip()
            tickers.append(symbol)
    return tickers

def fetch_stock_metrics(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    cashflow = stock.cashflow

    try:
        return {
            'Ticker': ticker,
            'Company': info.get('shortName'),
            'Market Cap': info.get('marketCap'),
            'P/E Ratio': info.get('trailingPE'),
            'EPS': info.get('trailingEps'),
            'P/B Ratio': info.get('priceToBook'),
            'Dividend Yield (%)': (info.get('dividendYield') or 0) * 100,
            'ROE (%)': (info.get('returnOnEquity') or 0) * 100,
            'Debt/Equity': info.get('debtToEquity'),
            'P/S Ratio': info.get('priceToSalesTrailing12Months'),
            'Operating Margin (%)': (info.get('operatingMargins') or 0) * 100,
            'EV/EBITDA': info.get('enterpriseToEbitda'),
            'Free Cash Flow': (
                cashflow.loc['Total Cash From Operating Activities'][0]
                - cashflow.loc['Capital Expenditures'][0]
                if 'Total Cash From Operating Activities' in cashflow.index and 'Capital Expenditures' in cashflow.index
                else None
            ),
            'Earnings Yield (%)': (
                (info['trailingEps'] / info['currentPrice']) * 100
                if info.get('trailingEps') and info.get('currentPrice') else None
            )
        }
    except Exception:
        return {'Ticker': ticker, 'Error': 'Data fetch error'}

def score_stock(row):
    score = 0
    if row['P/E Ratio'] and row['P/E Ratio'] < 20: score += 1
    if row['P/B Ratio'] and row['P/B Ratio'] < 3: score += 1
    if row['P/S Ratio'] and row['P/S Ratio'] < 2: score += 1
    if row['EV/EBITDA'] and row['EV/EBITDA'] < 10: score += 1
    if row['Earnings Yield (%)'] and row['Earnings Yield (%)'] > 5: score += 1
    if row['ROE (%)'] and row['ROE (%)'] > 15: score += 1
    if row['Operating Margin (%)'] and row['Operating Margin (%)'] > 10: score += 1
    if row['Debt/Equity'] and row['Debt/Equity'] < 1: score += 1
    if row['Free Cash Flow'] and row['Free Cash Flow'] > 0: score += 1
    return score

st.title("📈 Top 10 Active Stocks Analyzer")
tickers = get_top_10_stocks()

with st.spinner("Fetching financial data..."):
    data = [fetch_stock_metrics(t) for t in tickers]
    df = pd.DataFrame(data)
    df['Score'] = df.apply(score_stock, axis=1)
    df = df.sort_values(by='Score', ascending=False)

st.success("Analysis Complete!")

st.subheader("📊 Ranked Stocks by Score")
st.dataframe(df[['Ticker', 'Company', 'Score'] + [col for col in df.columns if col not in ['Ticker', 'Company', 'Score']]], height=500)

st.download_button("⬇ Download CSV", df.to_csv(index=False), "top_stocks.csv", "text/csv")
