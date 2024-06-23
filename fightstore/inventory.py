from fightstore.sheets import get_sheet
from pprint import pprint
import pandas as pd
from pprint import pprint
from .sheets import get_sheet

SHEET_NAME = "Simulation_Fight_Store"
sheet = get_sheet(SHEET_NAME)
prod_sheet = sheet.worksheet("products")
stock_sheet = sheet.worksheet("stock")

def get_inventory(sheet_name, category=None):
    sheet = get_sheet(sheet_name)
    inventory = sheet.worksheet("products")
    data = inventory.get_all_records()

    filtered_data = []
    for item in data:
        if category is None or item['Category'] == category:
            filtered_data.append({
                "Product Name": item.get("ProductName"),
                "Description": item.get("Description"),
                "Size": item.get("Size"),
                "Color": item.get("Color"),
                "ProductID": item.get("ProductID")
            })

    return filtered_data


 #This function returns the row data from our products page for a product to return its information   
def get_row_by_product_id(product_id):
    try:
        column_values = prod_sheet.col_values(1)
        row_index = column_values.index(product_id) + 1  
    except ValueError:
        print(f"Product ID '{product_id}' not found in the spreadsheet.")
        return None

    row_values = prod_sheet.row_values(row_index)

    return row_values
  
  #this function checks current stock for a specific product before continuing with the order
def check_stock(product_id, quantity):
    try:
        column_values = stock_sheet.col_values(1)
        row_index = column_values.index(product_id) + 1

        # Retrieves current stock count
        current_stock = int(stock_sheet.cell(row_index, 4).value)
        
        if current_stock >= quantity:
            return True, current_stock
        else:
            return False, current_stock
    except ValueError:
        print(f"Product ID '{product_id}' not found in the stock worksheet.")
        return False, 0
    except Exception as e:
        print(f"Error checking stock for Product ID '{product_id}': {e}")
        return False, 0