
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_ohlcv(symbol: str, days: int = 30) -> pd.DataFrame:
    '''
    Fetch past `days` of OHLCV data for a given NSE stock
    Converts symbol to Yahoo Finance format (e.g., TATAMOTORS.NS)
    '''
    end = datetime.today()
    start = end - timedelta(days=days * 2)  # Fetch a wider window to ensure trading days
    symbol_yahoo = symbol.upper() + ".NS"

    try:
        df = yf.download(symbol_yahoo, start=start, end=end)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print(f"Failed to fetch data for {symbol}: {e}")
        return pd.DataFrame()
