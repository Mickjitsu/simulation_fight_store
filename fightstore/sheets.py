import gspread
from google.oauth2.service_account import Credentials


def get_sheet(sheet_name):
    if not hasattr(get_sheet, "SHEET"):
        SCOPE = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        CREDS = Credentials.from_service_account_file('creds.json')
        SCOPED_CREDS = CREDS.with_scopes(SCOPE)
        GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
        get_sheet.SHEET = GSPREAD_CLIENT.open('Simulation_Fight_Store')
    return get_sheet.SHEET
