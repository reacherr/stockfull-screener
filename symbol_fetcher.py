import pandas as pd

def get_filtered_symbols():
    try:
        df500 = pd.read_csv("ind_nifty500list.csv")
        df500.columns = df500.columns.str.strip()
        symbols500 = df500["Symbol"].str.upper().tolist()

        df_all = pd.read_csv("EQUITY_L.csv")
        df_all.columns = df_all.columns.str.strip()

        filtered = df_all[df_all["SYMBOL"].isin(symbols500)]
        print(f"Nifty 500 symbols loaded: {len(symbols500)}")
        print(f"Filtered symbols (no market cap filter): {len(filtered)}")

        return filtered["SYMBOL"].tolist()
    except Exception as e:
        print(f"Error loading symbols: {e}")
        return []