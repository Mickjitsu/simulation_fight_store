from fightstore.sheets import get_sheet
from pprint import pprint

def get_inventory(sheet_name, category=None):
    sheet = get_sheet(sheet_name)
    inventory = sheet.worksheet("products")
    data = inventory.get_all_records()

    if category:
        data = [item for item in data if item['Category'] == category]
    
    filtered_data = [
        {
            "Product Name": item.get("ProductName"),
            "Description": item.get("Description"),
            "Size": item.get("Size"),
            "Color": item.get("Color"),
            "ProductID": item.get("ProductID")
        }
        for item in data
    ]
    return filtered_data

