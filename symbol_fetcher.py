import os
import requests
import pandas as pd
from datetime import datetime, timedelta

# Cache file paths
EQUITY_CSV = "cache/EQUITY_L.csv"
NIFTY500_CSV = "cache/NIFTY500.csv"
FILTERED_CSV = "cache/nifty500_filtered.csv"

# Create cache directory if needed
os.makedirs("cache", exist_ok=True)

def download_csv(url, path):
    """Download a CSV from the given URL with 3 retries."""
    for attempt in range(3):
        try:
            print(f"Downloading from {url} (Attempt {attempt+1})...")
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            with open(path, "wb") as f:
                f.write(resp.content)
            return True
        except Exception as e:
            print(f"Download attempt {attempt + 1} failed: {e}")
    return False

def should_refresh(path, days=7):
    """Return True if file is older than X days or does not exist."""
    if not os.path.exists(path):
        return True
    mod_time = datetime.fromtimestamp(os.path.getmtime(path))
    return datetime.now() - mod_time > timedelta(days=days)

def get_filtered_symbols():
    """Fetch filtered stock symbols from Nifty 500 (no market cap filter)."""
    
    nifty500_url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    equity_url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

    # Download CSVs if cache expired
    if should_refresh(NIFTY500_CSV):
        if not download_csv(nifty500_url, NIFTY500_CSV):
            raise Exception("Failed to fetch Nifty 500 list")

    if should_refresh(EQUITY_CSV):
        if not download_csv(equity_url, EQUITY_CSV):
            raise Exception("Failed to fetch NSE equity list")

    # Load and clean Nifty 500 symbols
    df500 = pd.read_csv(NIFTY500_CSV)
    df500.columns = df500.columns.str.strip()
    symbols500 = df500["Symbol"].str.upper().tolist()
    print(f"Nifty 500 symbols loaded: {len(symbols500)}")

    # Load NSE equity list
    df_all = pd.read_csv(EQUITY_CSV)
    df_all.columns = df_all.columns.str.strip()

    # Filter only by Nifty500 membership
    df_filtered = df_all[df_all["SYMBOL"].isin(symbols500)]

    # Save to cache
    df_filtered.to_csv(FILTERED_CSV, index=False)

    print(f"Filtered symbols (no market cap filter): {len(df_filtered)}")
    return df_filtered["SYMBOL"].tolist()
