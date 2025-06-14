
import pandas as pd

def is_vcp_pattern(df: pd.DataFrame) -> bool:
    '''
    VCP pattern detection:
    - Higher lows
    - Volume contraction
    '''
    if len(df) < 20:
        return False

    closes = df['Close'][-15:]
    volumes = df['Volume'][-15:]

    low_1 = min(closes[:5])
    low_2 = min(closes[5:10])
    low_3 = min(closes[10:])

    volume_contraction = volumes[:5].mean() > volumes[5:10].mean() > volumes[10:].mean()

    return low_1 < low_2 < low_3 and volume_contraction

def is_rocket_base(df: pd.DataFrame) -> bool:
    '''
    Rocket base:
    - Tight range (<=5%) over last 5 candles
    '''
    if len(df) < 5:
        return False

    recent = df[-5:]
    high = recent['High'].max()
    low = recent['Low'].min()

    consolidation_range = (high - low) / low

    return consolidation_range <= 0.05

def passes_consolidation(df: pd.DataFrame) -> bool:
    '''
    3–5 day consolidation logic
    '''
    if len(df) < 5:
        return False

    last_few = df[-5:]
    highs = last_few['High']
    lows = last_few['Low']

    return (highs.max() - lows.min()) / lows.min() < 0.07

def is_above_20dma(df: pd.DataFrame) -> bool:
    '''
    Confirm if close is above 20-day moving average
    '''
    if len(df) < 20:
        return False

    close = df['Close'].iloc[-1]
    dma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    return close > dma20
