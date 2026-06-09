"""Crypto Bot API service for cryptocurrency payments."""

import requests
from config.settings import settings


class CryptoBotService:
    """Service for integrating with Crypto Bot API for cryptocurrency payments."""

    def __init__(self):
        """Initialize Crypto Bot service with API key."""
        self.api_key = settings.CRYPTO_BOT_API_KEY
        self.base_url = "https://pay.crypt.bot/api"

    def generate_payment_address(self, amount: float, transaction_id: int, crypto_currency: str = None, crypto_network: str = None) -> str:
        """Generate a unique payment invoice that accepts any cryptocurrency.

        Args:
            amount: Amount in USD
            transaction_id: Transaction ID for reference
            crypto_currency: Deprecated - kept for backwards compatibility
            crypto_network: Deprecated - kept for backwards compatibility

        Returns:
            String format: "invoice_id|pay_url" or None if failed
        """
        if not self.api_key:
            print("Warning: CRYPTO_BOT_API_KEY not configured")
            # Return format: "invoice_id|pay_url" with sample data
            return f"{transaction_id}|https://t.me/CryptoBot?start=sample_invoice_{transaction_id}"

        try:
            headers = {
                "Crypto-Pay-API-Token": self.api_key
            }

            # Create invoice in USD that accepts ANY cryptocurrency
            # User can choose which crypto to pay with on CryptoBot payment page
            payload = {
                "currency_type": "fiat",
                "fiat": "USD",
                "amount": str(amount),
                "description": f"Wallet top-up #{transaction_id}",
                "paid_btn_name": "callback",
                "paid_btn_url": f"https://t.me/your_bot?start=payment_{transaction_id}",
                "allow_comments": False,
                "allow_anonymous": False
            }

            response = requests.post(
                f"{self.base_url}/createInvoice",
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print(f"CryptoBot createInvoice response: {data}")

                if not data.get("ok"):
                    print(f"CryptoBot API returned ok=false: {data}")
                    return None

                result = data.get("result", {})
                # Get invoice ID and payment URL
                invoice_id = result.get("invoice_id", "")  # Numeric ID for API calls
                invoice_hash = result.get("hash", "")      # Hash for URLs
                bot_invoice_url = result.get("bot_invoice_url", "")
                mini_app_url = result.get("mini_app_invoice_url", "")
                pay_url = bot_invoice_url or mini_app_url

                print(f"Created invoice: ID={invoice_id}, hash={invoice_hash}, url={pay_url}")

                # Store format: "invoice_id|pay_url" for later verification
                # We need the invoice_id for API calls, and pay_url for user payment
                if invoice_id and pay_url:
                    return f"{invoice_id}|{pay_url}"
                else:
                    print(f"Missing invoice_id or pay_url in response")
                    return None
            else:
                print(f"Crypto Bot API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Error generating crypto payment invoice: {e}")
            return None

    def check_payment_status(self, crypto_address: str, expected_amount: float) -> bool:
        """Check if payment has been received for the invoice.

        NOTE: This polling-based approach is a FALLBACK mechanism.
        For REAL-TIME payment notifications, use webhooks instead:
        - Run webhook_server.py alongside the bot
        - Configure webhook URL in @CryptoBot → Crypto Pay → My Apps → Webhooks
        - Webhooks provide instant payment confirmation vs. 30-second polling delay

        See webhook_server.py for implementation details.
        """
        if not self.api_key:
            print("Warning: CRYPTO_BOT_API_KEY not configured")
            return False

        try:
            # Extract invoice_id from stored format
            print(f"Checking payment for crypto_address: {crypto_address}")

            invoice_id = None

            # Format 1: "invoice_id|pay_url" (NEW FORMAT - numeric invoice_id)
            if "|" in crypto_address:
                invoice_id = crypto_address.split("|")[0]
                print(f"Extracted numeric invoice_id from new format: {invoice_id}")
            # Format 2: Old format - just URL (can't verify these, need to be manually confirmed)
            elif "https://t.me/CryptoBot" in crypto_address or "?start=" in crypto_address:
                print(f"⚠️ Old invoice format detected (URL-only). Cannot auto-verify.")
                print(f"   Admin must manually confirm this transaction.")
                return False
            else:
                invoice_id = crypto_address

            # Check if it's a sample address (no API key configured)
            if not invoice_id or "SAMPLE_" in str(invoice_id):
                print(f"Skipping check for sample/invalid address")
                return False

            headers = {
                "Crypto-Pay-API-Token": self.api_key,
                "Content-Type": "application/json"
            }

            # Get invoice details - CryptoBot API format
            # invoice_ids should be a comma-separated string of numeric IDs
            params = {}
            if invoice_id:
                # Ensure invoice_id is just the numeric ID
                params["invoice_ids"] = str(invoice_id).strip()

            print(f"Calling getInvoices with params: {params}")

            response = requests.get(
                f"{self.base_url}/getInvoices",
                headers=headers,
                params=params,
                timeout=10
            )

            print(f"CryptoBot API Response: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"CryptoBot Response Data: {data}")

                items = data.get("result", {}).get("items", [])

                if items:
                    invoice = items[0]
                    status = invoice.get("status")
                    paid_at = invoice.get("paid_at")
                    paid_amount = invoice.get("paid_amount")
                    paid_asset = invoice.get("paid_asset")

                    # Log all relevant fields for debugging
                    print(f"Invoice {invoice_id} details:")
                    print(f"  status: {status}")
                    print(f"  paid_at: {paid_at}")
                    print(f"  paid_amount: {paid_amount}")
                    print(f"  paid_asset: {paid_asset}")

                    # CryptoBot invoice statuses: active, paid, expired
                    # Primary check: status should be "paid"
                    if status == "paid":
                        print(f"✅ Invoice {invoice_id} is PAID (status=paid)")
                        return True

                    # Fallback check: if paid_at exists, payment was received
                    # (This handles cases where blockchain confirmation is pending)
                    if paid_at:
                        print(f"✅ Invoice {invoice_id} is PAID (paid_at={paid_at}, status={status})")
                        return True

                    print(f"⏳ Invoice {invoice_id} status: {status} (payment pending)")
                    return False
                else:
                    print(f"❌ No invoice found with ID: {invoice_id}")
                    return False
            else:
                error_text = response.text
                print(f"Crypto Bot API error checking status: {response.status_code} - {error_text}")
                return False

        except Exception as e:
            print(f"Error checking crypto payment status: {e}")
            import traceback
            traceback.print_exc()
            return False
