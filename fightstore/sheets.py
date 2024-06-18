import gspread
from google.oauth2.service_account import Credentials

def get_sheet(sheet_name):
    SCOPE = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
         ]
    CREDS = Credentials.from_service_account_file('fightstore/cred.json')
    SCOPED_CREDS = CREDS.with_scopes(SCOPE)
    GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
    SHEET = GSPREAD_CLIENT.open('Simulation_Fight_Store')
    return SHEET
