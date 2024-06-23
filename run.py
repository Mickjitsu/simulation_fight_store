from fightstore.inventory import get_inventory
import pandas as pd
from pprint import pprint
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import gspread
from fightstore.sheets import get_sheet
from fightstore.inventory import get_inventory, get_row_by_product_id, check_stock
from fightstore.sales import record_sale, generate_sale_id, get_price_by_product_id
from fightstore.ascii_welcome import ascii_welcome
from fightstore.send_message import send_message
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
    ascii_welcome()
    print("Welcome to Simulation Fightwear - BJJ FIGHT STORE")
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
    print("\nSelect a product by its index number or enter 'back' to return to the main menu:")
    for index, row in df_inventory.iterrows():
        print(f"{index}: {row['Product Name']} - {row['Description']} - {row['Size']} - {row['Color']}")

    while True:
        user_input = input("Enter the product index or 'back': ").strip().lower()
        
        if user_input == 'back':
            main_menu()
            return
        
        try:
            product_index = int(user_input)
            if product_index < 0 or product_index >= len(df_inventory):
                raise ValueError("Invalid index")
            
            product = df_inventory.iloc[product_index]
            
            quantity = int(input("Enter the quantity: "))
            
            process_selection(product, quantity)
            break  # Exit the loop after processing the selection
        except ValueError as e:
            print(f"Error: {e}. Please try again.")



def validate_phone_number(phone_number):
    # verification for phone number input to ensure it is a number and between 9 and 13 digits
     if re.fullmatch(r'\d{9,13}', phone_number):
        return True
     return False

#this function asks the customer to input their phone number in order to receive an order confirmation message   
def get_phone_number():
    phone_number = input("Please enter your phone number so that we can send your order confirmation via WhatsApp(9-13 digits including country code and no '+'): ").strip()
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
            
            # Calls stock sufficient function to ensure we have the correct stock before processing
            is_stock_sufficient, current_stock = check_stock(chosen_product, quantity)
            if is_stock_sufficient:
                while True:
                    purchase_choice = input("Would you like to purchase this product? (yes/no): ").strip().lower()
                    if purchase_choice == 'yes':
                        sale_id = generate_sale_id()
                        date_of_purchase = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        record_sale(sale_id, date_of_purchase, chosen_product, size, color, quantity, price, total_price)
                        print("Purchase successful!")

                        phone_number = get_phone_number()
                        send_message(phone_number, sale_id)
                        break
                    elif purchase_choice == 'no':
                        print("Sure thing, purchase cancelled.")
                        main_menu()
                        break
                    else:
                        print("Invalid input, please try again.")
                        retry_choice = input("Would you like to try again? (yes/no): ").strip().lower()
                        if retry_choice == 'no':
                            main_menu()
                            break
            else:
                print(f"Insufficient stock. Only {current_stock} units available.")
        else:
            print("Price not found.")
    else:
        print(f"Product ID '{chosen_product}' not found.")

if __name__ == "__main__":
    main_menu()
