"""Inline keyboard utilities for the Telegram bot."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.settings import settings


def create_main_menu_keyboard():
    """Create the main menu keyboard for users."""
    keyboard = [
        [InlineKeyboardButton("🛒 Products", callback_data="products")],
        [
            InlineKeyboardButton("💰 Top Up", callback_data="topup"),
            InlineKeyboardButton("Order History", callback_data="order_history")
        ],
        [
            InlineKeyboardButton("🧮 Availability", callback_data="availability"),
            InlineKeyboardButton("☎️ Support", callback_data="support")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_back_support_keyboard():
    """Create standard back and support buttons."""
    keyboard = [
        [
            InlineKeyboardButton("🔙 Back", callback_data="back"),
            InlineKeyboardButton("☎️ Support", callback_data="support")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_pagination_keyboard(items, page, total_pages, callback_prefix, back_button=True):
    """Create a paginated keyboard with items."""
    keyboard = []

    # Add item buttons - items should already be a list of button rows
    keyboard.extend(items)

    # Add pagination buttons if needed
    if total_pages > 1:
        pagination_row = []
        if page > 0:
            pagination_row.append(InlineKeyboardButton("◀️ Previous", callback_data=f"{callback_prefix}_page_{page-1}"))
        if page < total_pages - 1:
            pagination_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"{callback_prefix}_page_{page+1}"))
        if pagination_row:
            keyboard.append(pagination_row)

    # Add back and support buttons
    if back_button:
        keyboard.append([
            InlineKeyboardButton("🔙 Back", callback_data="back"),
            InlineKeyboardButton("☎️ Support", callback_data="support")
        ])

    return InlineKeyboardMarkup(keyboard)


def create_product_detail_keyboard(product_id, back_callback="back"):
    """Create keyboard for product details view with Buy Now button."""
    keyboard = [
        [InlineKeyboardButton("🛒 Buy Now", callback_data=f"buy_{product_id}")],
        [
            InlineKeyboardButton("🔙 Back", callback_data=back_callback),
            InlineKeyboardButton("☎️ Support", callback_data="support")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_quantity_keyboard(product_id):
    """Create keyboard for quantity confirmation."""
    keyboard = [
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_purchase")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_cancel_keyboard():
    """Create a simple cancel button keyboard."""
    keyboard = [[InlineKeyboardButton("☎️ Cancel", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)


def create_payment_method_keyboard():
    """Create payment method selection keyboard."""
    keyboard = [
        [InlineKeyboardButton("🪙 CryptoBot", callback_data="pay_crypto")],
        [InlineKeyboardButton("💳 Card", callback_data="pay_card")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_support_keyboard(support_username, channel_username):
    """Create support page keyboard with contact and community links."""
    keyboard = []

    if support_username:
        keyboard.append([InlineKeyboardButton("📞 Contact support", url=f"https://t.me/{support_username}")])

    if channel_username:
        keyboard.append([InlineKeyboardButton("🫂 Join My Community", url=f"https://t.me/{channel_username}")])

    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])

    return InlineKeyboardMarkup(keyboard)


def create_admin_main_menu_keyboard():
    """Create admin panel main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("📦 Product Management", callback_data="admin_products")],
        [InlineKeyboardButton("👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton("🛍 Order Management", callback_data="admin_orders")],
        [InlineKeyboardButton("⚙️ Store Settings", callback_data="admin_settings")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 Exit Admin", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_admin_product_menu_keyboard():
    """Create admin product management menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("➕ Create Product", callback_data="admin_create_product")],
        [InlineKeyboardButton("✏️ Edit Product", callback_data="admin_edit_product")],
        [InlineKeyboardButton("🔄 Restock Keys", callback_data="admin_restock_keys")],
        [InlineKeyboardButton("📁 Manage Categories", callback_data="admin_manage_categories")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_admin_category_menu_keyboard():
    """Create admin category management menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("➕ Create Category", callback_data="admin_create_category")],
        [InlineKeyboardButton("➕ Create Subcategory", callback_data="admin_create_subcategory")],
        [InlineKeyboardButton("✏️ Edit Category", callback_data="admin_edit_category")],
        [InlineKeyboardButton("✏️ Edit Subcategory", callback_data="admin_edit_subcategory")],
        [InlineKeyboardButton("📋 View Categories", callback_data="admin_view_categories")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_products")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_admin_user_menu_keyboard():
    """Create admin user management menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("👁 View Users", callback_data="admin_view_users")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_admin_order_menu_keyboard():
    """Create admin order management menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("📋 View All Orders", callback_data="admin_view_orders")],
        [InlineKeyboardButton("🚨 View Disputes", callback_data="admin_view_disputes")],
        [InlineKeyboardButton("✅ Manual Confirmation", callback_data="admin_confirm_order")],
        [InlineKeyboardButton("❌ Cancel Order", callback_data="admin_cancel_order")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_admin_settings_menu_keyboard():
    """Create admin store settings menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("💬 Welcome Message", callback_data="admin_welcome_msg")],
        [InlineKeyboardButton("🖼 Store Logo", callback_data="admin_store_logo")],
        [InlineKeyboardButton("📞 Support Username", callback_data="admin_support_username")],
        [InlineKeyboardButton("📢 Channel Username", callback_data="admin_channel_username")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_admin_broadcast_menu_keyboard():
    """Create admin broadcast menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("💬 Text Only Broadcast", callback_data="admin_broadcast_text")],
        [InlineKeyboardButton("🖼 Image + Text Broadcast", callback_data="admin_broadcast_image")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
