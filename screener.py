
import os
from dotenv import load_dotenv
from datetime import datetime

from fetch_technicals import fetch_ohlcv
from fetch_fundamentals import fetch_fundamentals
from pattern_detector import is_vcp_pattern, is_rocket_base, passes_consolidation, is_above_20dma
from telegram_sender import send_telegram_message
from sheets_logger import log_to_google_sheets

# Load environment variables
load_dotenv()

# Define a list of symbols to scan
SYMBOLS = ["TATAPOWER", "CMSINFO", "TCS", "PIDILITIND", "HDFCBANK"]

def format_telegram_message(results):
    message = "<b>📈 Swing Trade Picks – Auto Screener</b>\n"
    for stock in results:
        message += f"\n<b>{stock[0]}</b> ({stock[1]} tier)\nEntry: {stock[2]} | SL: {stock[3]} | Target: {stock[4]}\nSector: {stock[6]}\n{stock[5]}\n"
    return message

def calculate_levels(df):
    entry = round(df['Close'].iloc[-1], 2)
    stop = round(entry * 0.95, 2)
    target = round(entry * 1.1, 2)
    return f"₹{entry}", f"₹{stop}", f"₹{target}"

def check_eps_growth(eps_list):
    if len(eps_list) < 4:
        return False
    try:
        for i in range(1, 4):
            prev = eps_list[i]
            curr = eps_list[i - 1]
            if prev <= 0 or ((curr - prev) / prev) * 100 < 10:
                return False
        return True
    except:
        return False

def passes_fundamentals(symbol):
    data = fetch_fundamentals(symbol)
    if not data:
        return False, None, None, None, None, None

    roe = data.get("ROE", 0)
    roce = data.get("ROCE", 0)
    promoter = data.get("PromoterHolding", 0)
    eps_list = data.get("EPS", [])
    sector = data.get("Sector", "Unknown")
    sector_ok = data.get("SectorStrong", False)
    promoter_trend_ok = data.get("PromoterTrendOK", None)
    fii_trend_ok = data.get("FIITrendOK", None)

    if not check_eps_growth(eps_list):
        return False, None, None, None, None, None

    passes = roe > 15 and roce > 15 and promoter and promoter > 40
    reason = f"ROE: {roe}%, ROCE: {roce}%, Promoter Holding: {promoter}%, EPS QoQ Growth: OK"
    return passes, reason, sector, sector_ok, promoter_trend_ok, fii_trend_ok

def main():
    screener_results = []

    for symbol in SYMBOLS:
        fundamentals_passed, fundamentals_reason, sector, sector_ok, promoter_trend_ok, fii_trend_ok = passes_fundamentals(symbol)
        if not fundamentals_passed:
            continue

        df = fetch_ohlcv(symbol)
        if df.empty or len(df) < 20:
            continue

        if not passes_consolidation(df):
            continue

        is_vcp = is_vcp_pattern(df)
        is_rocket = is_rocket_base(df)
        above_dma = is_above_20dma(df)

        if is_vcp or is_rocket:
            entry, stop, target = calculate_levels(df)
            reason = "VCP pattern" if is_vcp else "Rocket base pattern"
            reason += " with 3–5 day consolidation | " + fundamentals_reason

            optional_flags = 0
            if above_dma:
                reason += " | Above 20DMA"
                optional_flags += 1
            if sector_ok:
                reason += " | Sector in Growth Phase"
                optional_flags += 1
            if promoter_trend_ok:
                reason += " | Promoter Holding Trend: Stable/Increasing"
                optional_flags += 1
            if fii_trend_ok:
                reason += " | FII Holding Trend: Increasing"
                optional_flags += 1

            if optional_flags >= 3:
                tier = "S"
            elif optional_flags == 2:
                tier = "A"
            else:
                tier = "B"

            screener_results.append([symbol, tier, entry, stop, target, reason, sector])

    if screener_results:
        send_telegram_message(format_telegram_message(screener_results))
        log_to_google_sheets(screener_results)
    else:
        print("No valid swing trade setups found today.")

if __name__ == "__main__":
    main()
