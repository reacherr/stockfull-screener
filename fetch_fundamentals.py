import time
import requests
from nsepython import nse_stock_financials, nse_eq
from requests.exceptions import RequestException

TRENDLYNE_HEADERS = {
    "X-RapidAPI-Host": "trendlyne-backend.p.rapidapi.com",
    "X-RapidAPI-Key": "your_rapidapi_key_here"  # Replace with real key
}

def fetch_eps_growth(symbol):
    try:
        data = nse_stock_financials(symbol)
        eps_data = data.get("financials", {}).get("quarterly_results", [])
        eps_values = [
            float(row.get("eps", 0))
            for row in eps_data[:4]
            if "eps" in row
        ]
        return eps_values if len(eps_values) >= 4 else None
    except Exception as e:
        print(f"EPS fetch failed for {symbol}: {e}")
        return None

def fetch_sector(symbol):
    try:
        profile = nse_eq(symbol)
        return profile.get("sector") or "Unknown"
    except Exception as e:
        print(f"Sector fetch failed for {symbol}: {e}")
        return "Unknown"

def fetch_trendlyne_fundamentals(symbol):
    try:
        url = f"https://trendlyne-backend.p.rapidapi.com/fundamentals/company_snapshot/{symbol}"
        resp = requests.get(url, headers=TRENDLYNE_HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"Trendlyne API error for {symbol}: {resp.status_code}")
            return None
        data = resp.json()

        roe = data.get("ratios", {}).get("ROE", 0)
        roce = data.get("ratios", {}).get("ROCE", 0)

        promoter_data = data.get("shareholding", {}).get("promoter_holding", [])
        fii_data = data.get("shareholding", {}).get("fii_holding", [])

        promoter_ok = False
        fii_ok = False

        if len(promoter_data) >= 4:
            deltas = [
                promoter_data[i]["value"] - promoter_data[i - 1]["value"]
                for i in range(1, 4)
            ]
            promoter_ok = all(d >= 0 for d in deltas)

        if len(fii_data) >= 4:
            deltas = [
                fii_data[i]["value"] - fii_data[i - 1]["value"]
                for i in range(1, 4)
            ]
            fii_ok = all(d >= 0 for d in deltas)

        return {
            "ROE": roe,
            "ROCE": roce,
            "PromoterTrendOK": promoter_ok,
            "FIITrendOK": fii_ok
        }

    except RequestException as e:
        print(f"Trendlyne fetch failed for {symbol}: {e}")
        return None

def fetch_fundamentals(symbol):
    time.sleep(1.2)
    eps_list = fetch_eps_growth(symbol)
    if not eps_list:
        return None

    sector = fetch_sector(symbol)
    trend_data = fetch_trendlyne_fundamentals(symbol)
    if not trend_data:
        return None

    return {
        "EPS": eps_list,
        "Sector": sector,
        "SectorStrong": True,  # Placeholder until real sector analysis added
        "ROE": trend_data["ROE"],
        "ROCE": trend_data["ROCE"],
        "PromoterTrendOK": trend_data["PromoterTrendOK"],
        "FIITrendOK": trend_data["FIITrendOK"]
    }