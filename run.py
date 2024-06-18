from fightstore.inventory import get_inventory
import pandas as pd

SHEET_NAME = "Simulation_Fight_Store"

def display_welcome_message():
    print("Welcome to Simulation Fightware!")
    print("Which products are you interested in?")
    print("1. GI")
    print("2. No-Gi")
    print("3. Misc")

def main_menu():
    display_welcome_message()
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == '1':
        display_category("GI")
    elif choice == '2':
        display_category("NO-GI")
    elif choice == '3':
        display_category("Misc")
    else:
        print("Invalid choice. Please try again.")
        main_menu()  

def display_category(category):
    inventory_data = get_inventory(SHEET_NAME, category)
    df_inventory = pd.DataFrame(inventory_data)
    print(f"\n{category} Inventory:")
    print(df_inventory)

if __name__ == "__main__":
    main_menu()
