from pprint import pprint
from datetime import datetime
from fightstore.sheets import get_sheet

SHEET_NAME = "Simulation_Fighit_Store"
sheet = get_sheet(SHEET_NAME)
prod_sheet = sheet.worksheet("products")
pricing_sheet = sheet.worksheet("pricing")
sales_sheet = sheet.worksheet("sales")
stock_sheet = sheet.worksheet("stock")
api_sheet = sheet.worksheet("api")


# This function records sales data on our sales worksheet
def record_sale(
    sale_id, date_of_purchase, product_id, size,
    color, quantity, price, total_price
):
    sales_sheet.append_row([
        sale_id, date_of_purchase, product_id,
        size, color, quantity, price, total_price
    ])

    try:
        # Finds the product via Index of productID in stock sheet
        column_values = stock_sheet.col_values(1)
        row_index = column_values.index(product_id) + 1

        # Updating stock count (4th column on sheet)
        current_stock = int(stock_sheet.cell(row_index, 4).value)
        updated_stock = current_stock - quantity

        # Ensuring stock doesn't go negative
        if updated_stock < 0:
            updated_stock = 0

        # Update the stock count in the worksheet
        stock_sheet.update_cell(row_index, 4, updated_stock)
        print(
            f"Stock updated successfully. New stock count for Product ID "
            f"'{product_id}': {updated_stock}"
        )
    except ValueError:
        print(f"Product ID '{product_id}' not found in the stock worksheet.")
    except Exception as e:
        print(f"Error updating stock for Product ID '{product_id}': {e}")


# This function generates a saleID that follows a format of 1101, 1102 etc
def generate_sale_id():
    sales_records = sales_sheet.get_all_records()
    if sales_records:
        try:
            last_sale_id = int(sales_records[-1]['Sale ID'])
            return last_sale_id + 1
        except (ValueError, KeyError) as e:
            print(f"Error extracting last sale ID: {e}")
            return 1101
    else:
        return 1101


# This function returns the price of a product
def get_price_by_product_id(product_id):
    try:
        column_values = pricing_sheet.col_values(1)
        row_index = column_values.index(product_id) + 1
    except ValueError:
        print(f"Product ID '{product_id}' not found in the pricing sheet.")
        return None

    row_values = pricing_sheet.row_values(row_index)

    price = row_values[3] if len(row_values) > 3 else None
    return price