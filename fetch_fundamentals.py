import time
import requests
import json
from bs4 import BeautifulSoup

TRENDLYNE_HEADERS = {
    "X-RapidAPI-Host": "trendlyne-backend.p.rapidapi.com",
    "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY")
}

def fetch_eps_growth(symbol):
    try:
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}"
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        resp = session.get(url, headers=headers, timeout=10)

        if resp.status_code != 200:
            print(f"[EPS] NSE API failed for {symbol}")
            return None

        data = resp.json()
        eps = float(data.get("metadata", {}).get("eps", 0))
        return [eps, eps * 1.1, eps * 1.2, eps * 1.3]  # Dummy growth for compatibility
    except Exception as e:
        print(f"[EPS] Failed for {symbol}: {e}")
        return None

def fetch_sector(symbol):
    try:
        url = f"https://www.nseindia.com/get-quotes/equity?symbol={symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html"
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        resp = session.get(url, headers=headers, timeout=10)

        if resp.status_code != 200:
            print(f"[Sector] NSE page failed for {symbol}")
            return "Unknown"

        soup = BeautifulSoup(resp.text, "html.parser")
        meta_tag = soup.find("meta", {"name": "description"})
        if meta_tag and "sector" in meta_tag.get("content", "").lower():
            return meta_tag["content"].split("sector")[-1].strip().split()[0]
        return "Unknown"
    except Exception as e:
        print(f"[Sector] Failed for {symbol}: {e}")
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

    except Exception as e:
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