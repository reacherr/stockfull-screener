import os
import gspread
import json
from datetime import datetime

def log_to_google_sheets(results):
    creds_json = os.environ.get("GOOGLE_SHEET_JSON")
    if not creds_json:
        print("Google credentials not found in environment.")
        return

    creds_dict = json.loads(creds_json)
    gc = gspread.service_account_from_dict(creds_dict)

    sheet = gc.open("Swing Trade Screener").sheet1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for stock in results:
        row = [now] + stock
        sheet.append_row(row)