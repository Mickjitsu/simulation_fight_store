from fightstore.inventory import get_inventory
import pandas as pd
from pprint import pprint

SHEET_NAME = "Simulation_Fight_Store"
prod_sheet = gc.open_by_key("Simulation_Fight_Store").worksheet("products")
def display_welcome_message():
    print("Welcome to Simulation Fightware!")
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
    
    get_row_by_product_id(chosen_product)

def get_row_by_product_id(product_id):

    column_values = prod_sheet.col_values(1)
    try:
        row_index = column_values.index(product_id) + 1  
    except ValueError:
        print(f"Product ID '{product_id}' not found in the spreadsheet.")
        return None

    row_values = sheet.row_values(row_index)

    return row_values

if __name__ == "__main__":
    main_menu()
