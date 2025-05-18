import requests
from django.conf import settings


PAYSTACK_SECRET = settings.PAYSTACK_SECRET_KEY

def create_subaccount(business_name, settlement_bank, account_number):
    """
    Create a subaccount on Paystack.
    """
    url = "https://api.paystack.co/subaccount"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET}",
        "Content-Type": "application/json",
    }
    
    data = {
        "business_name": business_name,
        "settlement_bank": settlement_bank,
        "account_number": account_number,
        "percentage_charge": 5.0,
    }
    response = requests.post(url, headers=headers, json=data)
    try:
        data = response.json()
    except ValueError:
        raise Exception("Paystack returned a non-JSON response")

    if not response.ok or not data.get("status"):
        raise Exception(f"Failed to create subaccount: {response.text}")

    return data