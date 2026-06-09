"""Check specific invoice status."""

import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python check_invoice.py <invoice_id>")
    print("Example: python check_invoice.py 37667214")
    sys.exit(1)

invoice_id = sys.argv[1]
api_key = os.getenv('CRYPTO_BOT_API_KEY')
base_url = "https://pay.crypt.bot/api"

headers = {
    "Crypto-Pay-API-Token": api_key,
    "Content-Type": "application/json"
}

print(f"Checking invoice: {invoice_id}")
print("=" * 60)

# Get invoice details
response = requests.get(
    f"{base_url}/getInvoices",
    headers=headers,
    params={"invoice_ids": str(invoice_id)},
    timeout=10
)

print(f"Status Code: {response.status_code}")
print(f"\nFull Response:")
print(response.json())

if response.status_code == 200:
    data = response.json()
    items = data.get("result", {}).get("items", [])

    if items:
        invoice = items[0]
        print("\n" + "=" * 60)
        print("INVOICE DETAILS:")
        print("=" * 60)
        print(f"Invoice ID: {invoice.get('invoice_id')}")
        print(f"Hash: {invoice.get('hash')}")
        print(f"Status: {invoice.get('status')}")
        print(f"Amount: {invoice.get('amount')} {invoice.get('asset')}")
        print(f"Created: {invoice.get('created_at')}")
        print()
        print("PAYMENT DETAILS:")
        print(f"Paid At: {invoice.get('paid_at', 'Not paid yet')}")
        print(f"Paid Amount: {invoice.get('paid_amount', 'N/A')} {invoice.get('paid_asset', '')}")
        print(f"Paid Anonymously: {invoice.get('paid_anonymously', False)}")
        print(f"Paid Unanonymously: {invoice.get('paid_unanonymously', False)}")
        print(f"Fee Amount: {invoice.get('fee_amount', 'N/A')} {invoice.get('fee_asset', '')}")

        # Check all fields
        print("\n" + "=" * 60)
        print("ALL FIELDS:")
        print("=" * 60)
        for key, value in invoice.items():
            print(f"{key}: {value}")
    else:
        print("No invoice found!")
