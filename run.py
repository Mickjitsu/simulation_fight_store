from fightstore.inventory import get_inventory
import pandas as pd
from pprint import pprint
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import gspread
from fightstore.sheets import get_sheet
from datetime import datetime
import re
import requests

SHEET_NAME = "Simulation_Fighit_Store"
sheet = get_sheet(SHEET_NAME)
prod_sheet = sheet.worksheet("products")
pricing_sheet = sheet.worksheet("pricing")
sales_sheet = sheet.worksheet("sales")
stock_sheet = sheet.worksheet("stock")
api_sheet = sheet.worksheet("api")

#this opening function welcomes the user to the store and displays their possible categories
def display_welcome_message():
    print("Welcome to Simulation Fightwear!")
    print("Which products are you interested in?")
    print("1. GI")
    print("2. No-Gi")
    print("3. Misc")

#this main menu function allows the user to choose their choice of category
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

#This function displays the products associated with a category
def display_category(category):
    inventory_data = get_inventory(SHEET_NAME, category)
    df_inventory = pd.DataFrame(inventory_data)
    select_product(df_inventory)

#this function shows the user their collection of products in a category and asks them to select a product by its index number
def select_product(df_inventory):
    print("\nSelect a product by its index number:")
    print(df_inventory[['Product Name', 'Description', 'Size', 'Color']].reset_index(drop=True))

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


def validate_phone_number(phone_number):
    # verification for phone number input to ensure it is a number and between 9 and 13 digits
     if re.fullmatch(r'\d{9,13}', phone_number):
        return True
     return False

#this function asks the customer to input their phone number in order to receive an order confirmation message   
def get_phone_number():
    phone_number = input("Please enter your phone number so that we can send your order confirmation via WhatsApp(10 digits-12 digits including country code and no '+'): ").strip()
    while not validate_phone_number(phone_number):
        print("Invalid phone number. Please enter a valid 10-12 digit phone number.")
        phone_number = input("Please enter your phone number (10-12 digits): ").strip()
    return phone_number

#main function for processing an order from a customer
def process_selection(product, quantity):
    print(f"\nYou have selected:\nProduct Name: {product['Product Name']}\nDescription: {product['Description']}\nQuantity: {quantity}\n ProductID: {product['ProductID']}\n Size:{product['Size']}")
    chosen_product = product['ProductID']
    
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

                 phone_number = get_phone_number()
                 send_message(phone_number, sale_id)

               else: 
                print("Purchase cancelled.")
            else:
                print(f"Insufficient stock. Only {current_stock} units available.")
        else:
            print("Price not found.")

#this function returns the API key to use in the send message function, so it isn't available directly in the platform
def get_api_key():
    try:
        api_key = api_sheet.cell(1, 1).value
        return api_key
    except Exception as e:
        print(f"Error retrieving API key: {e}")
        return None

#this function incorporates bird API to send a WhatsApp message with the order confirmation to the user
def send_message(phone_number, sale_id):
    phone_number_str = '+' + str(phone_number)
    url = "https://api.bird.com/workspaces/07817c84-ed36-45be-8d6d-b6d432ca8f0b/channels/10f849b9-3117-48aa-867b-c32a551fe815/messages"
    api_key = get_api_key()
    if not api_key:
        print("Failed to retrieve API key. Message not sent.")
        return
    
    payload = {
        "receiver": {
            "contacts": [
                {
                    "identifierValue": phone_number_str
                }
            ]
        },
        "template": {
            "projectId": "9d7dcf98-a234-4e45-8304-baabc5db4f50",
            "version": "latest",
            "locale": "en",
            "variables": {
                "order_number": str(sale_id)  
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        pprint(response.json())
    
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
  
    
#this function returns the price of a product by its productID on our pricing worksheet
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
#this functions generates a saleID that follows a format of 1101, 1102 etc 
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
#This function records sales data on our sales worksheet
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
