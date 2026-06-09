"""Helper utility functions for the Telegram bot."""

from datetime import datetime, timedelta
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import settings
from database import get_db_session, User

# In-memory cache for ban status (telegram_id: (is_banned, timestamp))
_ban_cache = {}
_BAN_CACHE_TTL = 30  # Cache ban status for 30 seconds


def is_admin(user_id: int) -> bool:
    """Check if a user is an admin based on Telegram ID."""
    return user_id == settings.ADMIN_TELEGRAM_ID


def admin_only(func):
    """Decorator to restrict handler access to admin only."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not is_admin(user_id):
            await update.message.reply_text("⛔ You don't have permission to access this command.")
            return
        return await func(update, context)
    return wrapper


def get_or_create_user(telegram_id: int, username: str = None):
    """Get existing user or create a new one in the database."""
    with get_db_session() as session:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()

        if not user:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            session.commit()
            session.refresh(user)

        return user


def format_price(price: float) -> str:
    """Format price to standard USD format."""
    return f"${price:.2f}"


def format_datetime(dt: datetime) -> str:
    """Format datetime to readable string."""
    return dt.strftime("%b %d, %Y")


def calculate_expiry_time(hours: int = 1) -> datetime:
    """Calculate expiry datetime from now."""
    return datetime.utcnow() + timedelta(hours=hours)


def paginate_items(items, page: int, page_size: int = 5):
    """Paginate a list of items."""
    start = page * page_size
    end = start + page_size
    total_pages = (len(items) + page_size - 1) // page_size

    return {
        'items': items[start:end],
        'page': page,
        'total_pages': total_pages,
        'has_next': page < total_pages - 1,
        'has_prev': page > 0
    }


def validate_amount(amount_str: str) -> tuple[bool, float, str]:
    """Validate user input for payment amount."""
    try:
        amount = float(amount_str.strip())
        if amount <= 0:
            return False, 0, "Amount must be greater than zero."
        if amount > 100000:
            return False, 0, "Amount is too large. Maximum is $100,000."
        return True, amount, ""
    except ValueError:
        return False, 0, "Invalid amount. Please enter a valid number."


def format_product_display(product, include_description=False) -> str:
    """Format product information for display."""
    text = f"""📦 Name: {product.name}
💰 Price: {format_price(product.price)}
📦 In Stock: {product.stock_count}"""

    if include_description and product.description:
        text += f"\n📝 Description: {product.description}"

    return text


async def notify_admin(context: ContextTypes.DEFAULT_TYPE, message: str):
    """Send notification message to admin."""
    try:
        await context.bot.send_message(
            chat_id=settings.ADMIN_TELEGRAM_ID,
            text=message
        )
    except Exception as e:
        print(f"Error notifying admin: {e}")


def build_availability_text(products_by_category) -> str:
    """Build availability page text with products grouped by category."""
    text = "💬 Our available Products\n\n"

    for category_name, products in products_by_category.items():
        text += f"📦━━━━━{category_name}━━━━━📦\n"
        for product in products:
            text += f"{product.name} | {format_price(product.price)} | Available: {product.stock_count}\n"
        text += "\n"

    return text


def parse_keys_from_text(text: str) -> list:
    """Parse keys from text input (one key per line)."""
    keys = [line.strip() for line in text.split('\n') if line.strip()]
    return keys


def check_user_banned(telegram_id: int) -> bool:
    """Check if a user is banned (with caching for performance)."""
    global _ban_cache

    # Check cache first
    if telegram_id in _ban_cache:
        cached_value, cached_time = _ban_cache[telegram_id]
        # If cache is still valid (within TTL), return cached value
        if (datetime.utcnow() - cached_time).total_seconds() < _BAN_CACHE_TTL:
            return cached_value

    # Cache miss or expired - query database
    with get_db_session() as session:
        # Use .scalar() for better performance - only fetch is_banned column
        is_banned = session.query(User.is_banned).filter_by(telegram_id=telegram_id).scalar()
        result = bool(is_banned) if is_banned is not None else False

        # Update cache
        _ban_cache[telegram_id] = (result, datetime.utcnow())

        return result


def clear_ban_cache(telegram_id: int = None):
    """Clear ban cache for a specific user or all users (called when ban status changes)."""
    global _ban_cache
    if telegram_id is None:
        _ban_cache.clear()
    elif telegram_id in _ban_cache:
        del _ban_cache[telegram_id]
