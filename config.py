"""
Configuration settings for the Telegram Store Bot
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

class BotConfig:
    """Bot configuration settings"""
    
    # Bot Settings
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    WEBHOOK_URL = os.getenv('NGROK_HTTPS_URL')
    
    # Store Settings
    STORE_CURRENCY = os.getenv('STORE_CURRENCY', 'USD')
    STORE_NAME = os.getenv('STORE_NAME', 'Telegram Store')
    
    # Database Settings
    DB_FILE = 'InDMDevDBShop.db'
    DB_BACKUP_INTERVAL = 3600  # 1 hour in seconds
    
    # Payment Settings
    NOWPAYMENTS_API_BASE = 'https://api.nowpayments.io/v1'
    COINGECKO_API_BASE = 'https://api.coingecko.com/api/v3'
    
    # Security Settings
    MAX_LOGIN_ATTEMPTS = 5
    SESSION_TIMEOUT = 3600  # 1 hour
    
    # File Upload Settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES = ['.txt', '.pdf', '.doc', '.docx']
    UPLOAD_FOLDER = 'uploads'
    KEYS_FOLDER = 'Keys'
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = 30
    MAX_REQUESTS_PER_HOUR = 1000
    
    # Logging Settings
    LOG_LEVEL = logging.INFO
    LOG_FILE = 'bot.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Cache Settings
    CACHE_TTL = 300  # 5 minutes
    CACHE_MAX_SIZE = 1000
    
    # Message Settings
    MAX_MESSAGE_LENGTH = 4096
    MAX_CAPTION_LENGTH = 1024
    
    # Product Settings
    MAX_PRODUCTS_PER_CATEGORY = 100
    MAX_CATEGORIES = 50
    MAX_PRODUCT_NAME_LENGTH = 100
    MAX_PRODUCT_DESCRIPTION_LENGTH = 1000
    
    # Order Settings
    ORDER_TIMEOUT = 1800  # 30 minutes
    MAX_ORDERS_PER_USER_PER_DAY = 10
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []
        
        if not cls.BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is not set")
        
        if not cls.WEBHOOK_URL:
            errors.append("NGROK_HTTPS_URL is not set")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    @classmethod
    def get_db_url(cls):
        """Get database connection URL"""
        return f"sqlite:///{cls.DB_FILE}"
    
    @classmethod
    def get_log_config(cls):
        """Get logging configuration"""
        return {
            'level': cls.LOG_LEVEL,
            'filename': cls.LOG_FILE,
            'maxBytes': cls.LOG_MAX_SIZE,
            'backupCount': cls.LOG_BACKUP_COUNT
        }

class APIConfig:
    """API configuration settings"""
    
    # Payment APIs
    NOWPAYMENTS_TIMEOUT = 30
    COINGECKO_TIMEOUT = 10
    
    # API Rate Limits
    NOWPAYMENTS_RATE_LIMIT = 100  # requests per minute
    COINGECKO_RATE_LIMIT = 100   # requests per minute
    
    # Retry Settings
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    @classmethod
    def get_headers(cls, api_key=None):
        """Get standard API headers"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TelegramStoreBot/1.0'
        }
        
        if api_key:
            headers['x-api-key'] = api_key
        
        return headers

class SecurityConfig:
    """Security configuration settings"""
    
    # Input Validation
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    
    # SQL Injection Prevention
    DANGEROUS_SQL_KEYWORDS = [
        'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER',
        'EXEC', 'EXECUTE', 'SCRIPT', 'UNION', 'SELECT'
    ]
    
    # XSS Prevention
    DANGEROUS_HTML_TAGS = [
        '<script>', '</script>', '<iframe>', '</iframe>',
        '<object>', '</object>', '<embed>', '</embed>'
    ]
    
    # File Upload Security
    DANGEROUS_FILE_EXTENSIONS = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
        '.vbs', '.js', '.jar', '.php', '.asp', '.aspx'
    ]
    
    @classmethod
    def is_safe_filename(cls, filename):
        """Check if filename is safe"""
        import os
        
        # Check for dangerous extensions
        _, ext = os.path.splitext(filename.lower())
        if ext in cls.DANGEROUS_FILE_EXTENSIONS:
            return False
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        return True

# Default configuration instance
config = BotConfig()

# Validate configuration on import
try:
    config.validate_config()
except ValueError as e:
    print(f"Configuration error: {e}")
    exit(1)