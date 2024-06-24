import requests
from pprint import pprint
from fightstore.sheets import get_sheet

SHEET_NAME = "Simulation_Fighit_Store"
sheet = get_sheet(SHEET_NAME)
api_sheet = sheet.worksheet("api")

# this function returns the API key to use in the send message function
def get_api_key():
    try:
        api_key = api_sheet.cell(1, 1).value
        return api_key
    except Exception as e:
        print(f"Error retrieving API key: {e}")
        return None

# this function incorporates bird API to send a WhatsApp confirmation
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

    if response.status_code == 202:
        print("Message sent successfully, keep an eye on your WhatsApp for a confirmation of your order!")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")