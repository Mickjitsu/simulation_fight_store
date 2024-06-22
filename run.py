from fightstore.inventory import get_inventory
import pandas as pd
from pprint import pprint
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import gspread
from fightstore.sheets import get_sheet
from datetime import datetime

SHEET_NAME = "Simulation_Fight_Store"
sheet = get_sheet(SHEET_NAME)
prod_sheet = sheet.worksheet("products")
pricing_sheet = sheet.worksheet("pricing")
sales_sheet = sheet.worksheet("sales")
stock_sheet = sheet.worksheet("stock")

def display_welcome_message():
    print("Welcome to Simulation Fightwear!")
    print("Which products are you interested in?")
    print("1. GI")
    print("2. No-Gi")
    print("3. Misc")

def main_menu():
    display_welcome_message()
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == '1' or choice == 'GI' or choice == 'Gi' or choice =='gi':
        display_category("GI")
    elif choice == '2' or choice == 'No-Gi' or choice == 'NO-GI' or choice == 'no-gi':
        display_category("NO-GI")
    elif choice == '3' or choice == 'misc' or choice == 'Misc' or choice == 'MISC':
        display_category("Misc")
    else:
        print("Invalid choice. Please try again.")
        main_menu()  

def display_category(category):
    inventory_data = get_inventory(SHEET_NAME, category)
    df_inventory = pd.DataFrame(inventory_data)
    pprint(f"\n{category} Inventory:")
    pprint(df_inventory)
    select_product(df_inventory)

def select_product(df_inventory):
    print("\nSelect a product by its index number:")
    print(df_inventory[['Product Name', 'Description', 'Size', 'Color']].reset_index())

    try:
        product_index = int(input("Enter the product index: "))
        if product_index < 0 or product_index >= len(df_inventory):
            raise ValueError("Invalid index")
        
        product = df_inventory.iloc[product_index]
        
        quantity = int(input("Enter the quantity: "))
        
        process_selection(product, quantity)
    except ValueError as e:
        print(f"Error: {e}. Please try again.")
        select_product(df_inventory)

        print(product_index)

def process_selection(product, quantity):
    print(f"\nYou have selected:\nProduct Name: {product['Product Name']}\nDescription: {product['Description']}\nQuantity: {quantity}\n ProductID: {product['ProductID']}\n Size:{product['Size']}")
    chosen_product = product['ProductID']
    print(chosen_product)
    
    row_values = get_row_by_product_id(chosen_product)
    if row_values:
        product_name, category, description, size, color = row_values[:5]  
        price = get_price_by_product_id(chosen_product)
        if price is not None:
            total_price = float(price) * quantity
            print(f"Price per unit: {price}")
            print(f"Total price: {total_price}")
            
            #calls stuck sufficient function to ensure we have the correct stock before processing
            is_stock_sufficient, current_stock = check_stock(chosen_product, quantity)
            if is_stock_sufficient:
               purchase_choice = input("Would you like to purchase this product? (yes/no): ").strip().lower()
               if purchase_choice == 'yes':
                 sale_id = generate_sale_id()
                 date_of_purchase = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                 record_sale(sale_id, date_of_purchase, chosen_product, size, color, quantity, price, total_price)
                 print("Purchase successful!")
               else: 
                print("Purchase cancelled.")
            else:
                print(f"Insufficient stock. Only {current_stock} units available.")
        else:
            print("Price not found.")

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

    
def get_row_by_product_id(product_id):
    try:
        column_values = prod_sheet.col_values(1)
        print(f"Column values for Product IDs: {column_values}")  
        row_index = column_values.index(product_id) + 1  
        print(f"Row index for Product ID '{product_id}': {row_index}")  
    except ValueError:
        print(f"Product ID '{product_id}' not found in the spreadsheet.")
        return None

    row_values = prod_sheet.row_values(row_index)
    print(f"Row values for Product ID '{product_id}': {row_values}")  

    return row_values
  
    

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

def generate_sale_id():
    sales_records = sales_sheet.get_all_records()
    print(f"Sales records: {sales_records}")  
    if sales_records:
        try:
            
            last_sale_id = int(sales_records[-1]['Sale ID'])
            return last_sale_id + 1
        except (ValueError, KeyError) as e:
            print(f"Error extracting last sale ID: {e}")
            return 1101
    else:
        return 1101

def record_sale(sale_id, date_of_purchase, product_id, size, color, quantity, price, total_price):
    sales_sheet.append_row([sale_id, date_of_purchase, product_id, size, color, quantity, price, total_price])

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
        print(f"Stock updated successfully. New stock count for Product ID '{product_id}': {updated_stock}")
    except ValueError:
        print(f"Product ID '{product_id}' not found in the stock worksheet.")
    except Exception as e:
        print(f"Error updating stock for Product ID '{product_id}': {e}")

if __name__ == "__main__":
    main_menu()
