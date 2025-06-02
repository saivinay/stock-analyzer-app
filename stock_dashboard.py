import streamlit as st
import pandas as pd
import requests

# Replace with your actual FMP API key
API_KEY = 'eLZVIiG9DSAFlfqQ48Q7vxcfIDF3lFv2'

# List of stock tickers
TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'BRK.B', 'UNH', 'JNJ']

# Function to fetch stock data
def fetch_stock_data(ticker):
    base_url = 'https://financialmodelingprep.com/api/v3'
    endpoints = {
        'quote': f'{base_url}/quote/{ticker}?apikey={API_KEY}',
        'profile': f'{base_url}/profile/{ticker}?apikey={API_KEY}',
        'ratios': f'{base_url}/ratios-ttm/{ticker}?apikey={API_KEY}'
    }
    data = {}
    try:
        quote_response = requests.get(endpoints['quote']).json()
        profile_response = requests.get(endpoints['profile']).json()
        ratios_response = requests.get(endpoints['ratios']).json()

        if quote_response and isinstance(quote_response, list):
            quote = quote_response[0]
            data['Price'] = quote.get('price')
            data['Market Cap'] = quote.get('marketCap')
        else:
            st.warning(f"No quote data for {ticker}")
            return None

        if profile_response and isinstance(profile_response, list):
            profile = profile_response[0]
            data['PE Ratio'] = profile.get('pe')
            data['EPS'] = profile.get('eps')
            data['P/B Ratio'] = profile.get('priceToBookRatio')
            data['Dividend Yield'] = profile.get('lastDiv')
        else:
            st.warning(f"No profile data for {ticker}")
            return None

        if ratios_response and isinstance(ratios_response, list):
            ratios = ratios_response[0]
            data['ROE'] = ratios.get('returnOnEquityTTM')
            data['Debt to Equity'] = ratios.get('debtEquityRatioTTM')
            data['P/S Ratio'] = ratios.get('priceToSalesRatioTTM')
            data['EV/EBITDA'] = ratios.get('evToEbitdaTTM')
            data['Operating Margin'] = ratios.get('operatingProfitMarginTTM')
            data['FCF Margin'] = ratios.get('freeCashFlowMarginTTM')
        else:
            st.warning(f"No ratios data for {ticker}")
            return None

        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Function to calculate score
def calculate_score(row):
    score = 0
    try:
        if pd.notnull(row['EPS']) and row['EPS'] > 0:
            score += 1
        if pd.notnull(row['ROE']) and row['ROE'] > 0.15:
            score += 1
        if pd.notnull(row['Operating Margin']) and row['Operating Margin'] > 0.2:
            score += 1
        if pd.notnull(row['FCF Margin']) and row['FCF Margin'] > 0.1:
            score += 1
        if pd.notnull(row['Debt to Equity']) and row['Debt to Equity'] < 1:
            score += 1
    except Exception as e:
        st.error(f"Error calculating score for {row['Ticker']}: {e}")
    return score

# Main Streamlit app
def main():
    st.title("Stock Analyzer App")

    data_list = []
    for ticker in TICKERS:
        st.write(f"Fetching data for {ticker}...")
        data = fetch_stock_data(ticker)
        if data:
            data['Ticker'] = ticker
            data_list.append(data)

    if data_list:
        df = pd.DataFrame(data_list)
        df['Score'] = df.apply(calculate_score, axis=1)

        # Format columns
        df['Price'] = df['Price'].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else 'N/A')
        df['Market Cap'] = df['Market Cap'].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else 'N/A')
        df['PE Ratio'] = df['PE Ratio'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else 'N/A')
        df['EPS'] = df['EPS'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else 'N/A')
        df['P/B Ratio'] = df['P/B Ratio'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else 'N/A')
        df['Dividend Yield'] = df['Dividend Yield'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else 'N/A')
        df['ROE'] = df['ROE'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else 'N/A')
        df['Debt to Equity'] = df['Debt to Equity'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else 'N/A')
        df['P/S Ratio'] = df['P/S Ratio'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else 'N/A')
        df['EV/EBITDA'] = df['EV/EBITDA'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else 'N/A')
        df['Operating Margin'] = df['Operating Margin'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else 'N/A')
        df['FCF Margin'] = df['FCF Margin'].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else 'N/A')

        st.dataframe(df)
    else:
        st.error("No data available to display.")

if __name__ == "__main__":
    main()
