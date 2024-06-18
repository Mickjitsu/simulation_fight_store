from fightstore.sheets import get_sheet

def get_inventory(sheet_name, category=None):
    sheet = get_sheet(sheet_name)
    inventory = sheet.worksheet("products")
    data = inventory.get_all_records()

    if category:
        data = [item for item in data if item['Category'] == category]

    return data

