
import requests
from bs4 import BeautifulSoup

PERFORMING_SECTORS = [
    "IT", "Information Technology", "Software", "Telecom Services",
    "Auto", "Automobile", "Auto Ancillaries", "Electric Vehicles",
    "Capital Goods", "Infrastructure", "Industrial Machinery", "Engineering",
    "FMCG", "Consumer Goods", "Food Processing", "Beverages",
    "Banks", "Private Banks", "Public Sector Banks", "NBFC", "Financial Services",
    "Pharma", "Healthcare", "Hospitals", "Biotechnology",
    "Chemical", "Specialty Chemicals", "Agro Chemicals", "Fertilizers",
    "Energy", "Power", "Renewable Energy", "Green Energy", "Oil & Gas",
    "Real Estate", "Construction", "Cement", "Housing",
    "Defence", "Aerospace", "Railways", "Marine",
    "Textiles", "Apparel", "Retail", "Consumer Discretionary"
]

def check_promoter_trend(values):
    if len(values) < 2:
        return None
    return all(values[i] >= values[i+1] for i in range(len(values) - 1))

def check_fii_trend(data_rows):
    fii_trend = []
    for row in data_rows:
        if "fii" in row.text.lower() or "foreign" in row.text.lower():
            cells = row.find_all("td")[1:]
            for cell in cells:
                try:
                    val = float(cell.text.replace("%", "").strip())
                    fii_trend.append(val)
                except:
                    continue
            break
    if len(fii_trend) >= 2:
        return all(fii_trend[i] <= fii_trend[i-1] for i in range(1, len(fii_trend)))
    return None

def fetch_fundamentals(symbol: str) -> dict:
    url = f"https://www.screener.in/company/{symbol}/consolidated/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch data for {symbol}")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")

        # Overview ratios
        overview = {}
        for row in soup.select(".company-ratios table tr"):
            cells = row.find_all("td")
            if len(cells) == 2:
                key = cells[0].text.strip()
                value = cells[1].text.strip()
                overview[key] = value

        roe = float(overview.get("ROE", "0").replace("%", "").strip() or 0)
        roce = float(overview.get("ROCE", "0").replace("%", "").strip() or 0)

        # Sector info
        sector_tag = soup.select_one(".breadcrumb a[href*='/sector/']")
        sector = sector_tag.text.strip() if sector_tag else "Unknown"
        sector_ok = any(s.lower() in sector.lower() for s in PERFORMING_SECTORS)

        # Promoter + FII holdings
        promoter_trend = []
        fii_trend_ok = None
        promoter_section = soup.find("section", id="shareholding")
        if promoter_section:
            rows = promoter_section.select("tbody tr")
            for row in rows:
                if "promoter" in row.text.lower():
                    cells = row.find_all("td")
                    for i in range(1, len(cells)):
                        try:
                            val = float(cells[i].text.replace("%", "").strip())
                            promoter_trend.append(val)
                        except:
                            continue
                if fii_trend_ok is None:
                    fii_trend_ok = check_fii_trend(rows)

        promoter_trend = promoter_trend[:5]
        promoter_trend_ok = check_promoter_trend(promoter_trend)
        latest_promoter_holding = promoter_trend[0] if promoter_trend else None

        # EPS extraction
        eps_values = []
        tables = soup.find_all("table")
        for table in tables:
            if "EPS" in table.text:
                rows = table.find_all("tr")
                for row in rows:
                    if "EPS" in row.text:
                        cells = row.find_all("td")[1:]
                        for cell in cells:
                            try:
                                eps = float(cell.text.strip())
                                eps_values.append(eps)
                            except:
                                continue
                        break
                break

        return {
            "ROE": roe,
            "ROCE": roce,
            "PromoterHolding": latest_promoter_holding,
            "PromoterTrend": promoter_trend,
            "PromoterTrendOK": promoter_trend_ok,
            "EPS": eps_values[:4],
            "Sector": sector,
            "SectorStrong": sector_ok,
            "FIITrendOK": fii_trend_ok
        }

    except Exception as e:
        print(f"Error scraping fundamentals for {symbol}: {e}")
        return {}
