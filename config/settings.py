"""Configuration settings loader from environment variables."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Stores all configuration settings for the bot."""

    # Telegram Bot Settings
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_TELEGRAM_ID = int(os.getenv('ADMIN_TELEGRAM_ID', 0))
    ADMIN_TELEGRAM_USERNAME = os.getenv('ADMIN_TELEGRAM_USERNAME', '')

    # Database Settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot_database.db')

    # Crypto Payment Settings
    CRYPTO_BOT_API_KEY = os.getenv('CRYPTO_BOT_API_KEY', '')

    # Telegram Payments (Card) Settings
    # Provider token from @BotFather → your bot → Payments → connect a provider.
    TELEGRAM_PROVIDER_TOKEN = os.getenv('TELEGRAM_PROVIDER_TOKEN', '')
    # Currency the card invoice is charged in. The numeric amount equals the USD
    # top-up value, so this must be a USD-denominated provider for amounts to match.
    PAYMENT_CURRENCY = os.getenv('PAYMENT_CURRENCY', 'USD')

    # Application Settings
    PAYMENT_EXPIRY_HOURS = 0.5  # Payment order expiration time (30 minutes)
    PAYMENT_CHECK_INTERVAL = 30  # Seconds between payment verification checks

    # Asset Storage
    ASSETS_DIR = 'assets'
    LOGOS_DIR = os.path.join(ASSETS_DIR, 'logos')
    PRODUCTS_DIR = os.path.join(ASSETS_DIR, 'products')


# Create settings instance
settings = Settings()


def validate_settings():
    """Validates that all required settings are configured."""
    if not settings.BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required in .env file")

    if not settings.ADMIN_TELEGRAM_ID:
        raise ValueError("ADMIN_TELEGRAM_ID is required in .env file")

    print("[OK] Configuration validated successfully")
