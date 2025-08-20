"""
Utility functions for the Telegram Store Bot
"""

import re
import logging
from typing import Optional, Union
from localization import get_text

logger = logging.getLogger(__name__)

class InputValidator:
    """Input validation and sanitization utilities"""
    
    @staticmethod
    def validate_user_id(user_id: Union[str, int]) -> Optional[int]:
        """Validate and convert user ID to integer"""
        try:
            user_id = int(user_id)
            if user_id > 0:
                return user_id
            return None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_username(username: str) -> Optional[str]:
        """Validate and sanitize username"""
        if not username or not isinstance(username, str):
            return None
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';]', '', username.strip())
        
        # Check if username is reasonable length
        if 1 <= len(sanitized) <= 50:
            return sanitized
        return None
    
    @staticmethod
    def validate_product_number(product_number: Union[str, int]) -> Optional[int]:
        """Validate product number"""
        try:
            product_number = int(product_number)
            if 10000000 <= product_number <= 99999999:  # 8 digits
                return product_number
            return None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_price(price: Union[str, int, float]) -> Optional[float]:
        """Validate price value"""
        try:
            price = float(price)
            if price >= 0:
                return round(price, 2)
            return None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def validate_quantity(quantity: Union[str, int]) -> Optional[int]:
        """Validate quantity value"""
        try:
            quantity = int(quantity)
            if quantity >= 0:
                return quantity
            return None
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> Optional[str]:
        """Sanitize text input"""
        if not text or not isinstance(text, str):
            return None
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';]', '', text.strip())
        
        # Check length
        if len(sanitized) <= max_length:
            return sanitized
        return sanitized[:max_length]

class SecurityUtils:
    """Security-related utility functions"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid and safe"""
        if not url or not isinstance(url, str):
            return False
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    @staticmethod
    def sanitize_sql_input(value: str) -> str:
        """Basic SQL injection prevention"""
        if not value:
            return ""
        
        # Remove or escape potentially dangerous SQL characters
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        sanitized = str(value)
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()

class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def handle_database_error(chat_id: int, error: Exception, operation: str) -> str:
        """Handle database-related errors"""
        logger.error(f"Database error in {operation}: {error}")
        return get_text(chat_id, 'database_error')
    
    @staticmethod
    def handle_api_error(chat_id: int, error: Exception, api_name: str) -> str:
        """Handle API-related errors"""
        logger.error(f"API error in {api_name}: {error}")
        return get_text(chat_id, 'api_error').format(api_name=api_name)
    
    @staticmethod
    def handle_user_error(chat_id: int, error: Exception, operation: str) -> str:
        """Handle user input errors"""
        logger.warning(f"User error in {operation}: {error}")
        return get_text(chat_id, 'user_error')

class MessageFormatter:
    """Message formatting utilities"""
    
    @staticmethod
    def format_product_info(chat_id: int, product_data: dict) -> str:
        """Format product information for display"""
        return get_text(chat_id, 'product_details').format(
            name=product_data.get('name', 'N/A'),
            price=product_data.get('price', 0),
            currency=product_data.get('currency', 'USD'),
            description=product_data.get('description', 'No description'),
            quantity=product_data.get('quantity', 0),
            category=product_data.get('category', 'Uncategorized')
        )
    
    @staticmethod
    def format_order_info(chat_id: int, order_data: dict) -> str:
        """Format order information for display"""
        return get_text(chat_id, 'order_details').format(
            id=order_data.get('id', 'N/A'),
            product_name=order_data.get('product_name', 'N/A'),
            price=order_data.get('price', 0),
            currency=order_data.get('currency', 'USD'),
            date=order_data.get('date', 'N/A'),
            status=order_data.get('status', 'N/A')
        )
    
    @staticmethod
    def format_error_message(chat_id: int, error_type: str, user_friendly: bool = True) -> str:
        """Format error messages for users"""
        if user_friendly:
            return get_text(chat_id, 'error_message').format(error_type=error_type)
        return get_text(chat_id, 'error_message_simple').format(error_type=error_type)

class CacheManager:
    """Simple in-memory cache manager"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key: str):
        """Get value from cache"""
        return self.cache.get(key)
    
    def set(self, key: str, value, ttl: int = 300):
        """Set value in cache with TTL (Time To Live)"""
        import time
        self.cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
    
    def is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        import time
        if key not in self.cache:
            return True
        return time.time() > self.cache[key]['expires']
    
    def clear_expired(self):
        """Clear expired cache entries"""
        import time
        current_time = time.time()
        expired_keys = [
            key for key, data in self.cache.items()
            if current_time > data['expires']
        ]
        for key in expired_keys:
            del self.cache[key]

# Global cache instance
cache = CacheManager()