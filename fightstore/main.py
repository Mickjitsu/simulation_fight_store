from fightstore.inventory import (
    get_inventory, get_row_by_product_id, check_stock
)
import pandas as pd
from pprint import pprint
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import gspread
from fightstore.sheets import get_sheet
from fightstore.sales import (
    record_sale, generate_sale_id, get_price_by_product_id
)
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


def display_welcome_message():
    ascii_welcome()
    print("Welcome to Simulation Fightwear - BJJ FIGHT STORE")
    print("Which products are you interested in?")
    print("1. GI")
    print("2. No-Gi")
    print("3. Misc")


def main_menu():
    display_welcome_message()
    choice = input("Enter your choice (1-3): ").lower()
    if choice in ['1', 'gi']:
        display_category("GI")
    elif choice in ['2', 'no-gi']:
        display_category("NO-GI")
    elif choice in ['3', 'misc']:
        display_category("Misc")
    else:
        print("Invalid choice. Please try again.")
        main_menu()


def display_category(category):
    inventory_data = get_inventory(SHEET_NAME, category)
    df_inventory = pd.DataFrame(inventory_data)
    select_product(df_inventory)


def select_product(df_inventory):
    print("\nSelect a product by its index number or enter 'back'"
          "to return to the main menu:")
    for index, row in df_inventory.iterrows():
        print(f"{index}: {row['Product Name']} - {row['Description']} "
              "- {row['Size']} - {row['Color']}")
    while True:
        user_input = input("Enter the product index "
                           "or 'back': ").strip().lower()
        if user_input == 'back':
            main_menu()
            return
        try:
            product_index = int(user_input)
            if product_index < 0 or product_index >= len(df_inventory):
                raise ValueError("Invalid index")
            product = df_inventory.iloc[product_index]
            while True:  
                quantity = int(input("Enter the quantity: "))
                if quantity <= 0:
                    print("Quantity must be greater than 0. Please try again.")
                else:
                    process_selection(product, quantity)
                    return  
        except ValueError as e:
            print(f"Error: {e}. Please try again.")



def validate_phone_number(phone_number):
    return bool(re.fullmatch(r'\d{9,13}', phone_number))


def get_phone_number():
    phone_number = input("Please enter your phone number "
                         "(9-13 digits): ").strip()
    while not validate_phone_number(phone_number):
        print("Invalid phone number. Please enter"
              "a valid 9-13 digit phone number.")
        phone_number = input("Please enter your phone "
                             "number (9-13 digits): ").strip()
    return phone_number


def process_selection(product, quantity):
    print(f"\nYou have selected:\n"
          f"Product Name: {product['Product Name']}\n"
          f"Description: {product['Description']}\n"
          f"Quantity: {quantity}\n"
          f"ProductID: {product['ProductID']}\n"
          f"Size: {product['Size']}")

    chosen_product = product['ProductID']
    row_values = get_row_by_product_id(chosen_product)
    if row_values:
        product_name, category, description, size, color = row_values[:5]
        price = get_price_by_product_id(chosen_product)
        if price is not None:
            total_price = float(price) * quantity
            print(f"Price per unit: {price}")
            print(f"Total price: {total_price}")
            is_stock_sufficient, current_stock = (
                check_stock(chosen_product, quantity)
                )
            if is_stock_sufficient:
                while True:
                    purchase_choice = input("Would you like to purchase "
                                            "this product? (yes/no): ").strip().lower()
                    if purchase_choice == 'yes':
                        sale_id = generate_sale_id()
                        date_of_purchase = (
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            )
                        record_sale(sale_id, date_of_purchase, chosen_product,
                                    size, color, quantity, price, total_price)
                        print("Purchase successful!")
                        phone_number = get_phone_number()
                        send_message(phone_number, sale_id)
                        break
                    elif purchase_choice == 'no':
                        print("Sure thing, purchase cancelled. "
                              "Returning to the main menu!")
                        main_menu()
                        break
                    else:
                        print("Invalid input, please try again.")
            else:
                print(f"Insufficient stock. Only {current_stock} units "
                      "available.Returning to the main menu.")
                main_menu()
        else:
            print("Price not found, returning to main menu.")
            main_menu()
    else:
        print(f"Product ID '{chosen_product}' not found"
              ", returning to main menu.")
        main_menu()