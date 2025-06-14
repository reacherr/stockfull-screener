
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

GSHEET_ID = os.getenv("GSHEET_ID")
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDS_JSON", "google_service_account.json")

def log_to_google_sheets(data: list):
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GSHEET_ID).sheet1

        # Header setup if empty
        if sheet.row_count < 1:
            sheet.append_row(["Date", "Stock", "Tier", "Entry", "Stop Loss", "Target", "Reason"])

        today = datetime.now().strftime("%Y-%m-%d")
        for row in data:
            sheet.append_row([today] + row)
        print("Data logged to Google Sheets.")
    except Exception as e:
        print(f"Error logging to Google Sheets: {e}")
