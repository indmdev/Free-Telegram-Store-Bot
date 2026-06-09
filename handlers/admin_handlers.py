"""Admin panel command and callback handlers."""

import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import func
from database import (
    get_db_session, User, Category, Subcategory, Product, ProductKey,
    Order, OrderItem, Settings, Broadcast, ProductType, OrderStatus, DisputeStatus
)
from utils import (
    is_admin, admin_only, format_price,
    create_admin_main_menu_keyboard, create_admin_product_menu_keyboard,
    create_admin_category_menu_keyboard, create_admin_user_menu_keyboard,
    create_admin_order_menu_keyboard, create_admin_settings_menu_keyboard,
    create_admin_broadcast_menu_keyboard, parse_keys_from_text, clear_ban_cache
)
from config.settings import settings as app_settings
from telegram.ext import ConversationHandler

# Conversation states for restock keys
WAITING_FOR_KEYS = 1


@admin_only
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - show admin panel."""
    await update.message.reply_text(
        "🔐 Admin Panel\n\nSelect an option:",
        reply_markup=create_admin_main_menu_keyboard()
    )


async def admin_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin menu callback - return to admin main menu."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    await query.edit_message_text(
        "🔐 Admin Panel\n\nSelect an option:",
        reply_markup=create_admin_main_menu_keyboard()
    )


async def admin_restock_keys_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin restock keys button - show product selection."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    with get_db_session() as session:
        # Get all KEY type products
        products = session.query(Product).filter_by(product_type=ProductType.KEY).all()

        if not products:
            await query.edit_message_text(
                "❌ No KEY products found. Please create a product first.",
                reply_markup=create_admin_product_menu_keyboard()
            )
            return

        # Build product selection keyboard
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = []
        for product in products[:10]:  # Show first 10
            keyboard.append([
                InlineKeyboardButton(
                    f"📦 {product.name} (Stock: {product.stock_count})",
                    callback_data=f"select_product_{product.id}"
                )
            ])

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_products")])

        await query.edit_message_text(
            "🔄 Select a product to restock:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def admin_select_product_restock_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product selection for restocking."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    # Extract product ID from callback data
    product_id = int(query.data.split("_")[2])

    # Store product ID in context for later use
    context.user_data['restock_product_id'] = product_id

    with get_db_session() as session:
        product = session.query(Product).filter_by(id=product_id).first()

        if not product:
            await query.edit_message_text(
                "❌ Product not found.",
                reply_markup=create_admin_product_menu_keyboard()
            )
            return

        message = f"""🔄 Restocking: {product.name}
Current Stock: {product.stock_count}

📤 Upload a .txt file with keys (one per line)
OR
✍️ Paste keys directly (one per line)

Example:
KEY1-XXXX-XXXX-XXXX
KEY2-XXXX-XXXX-XXXX
KEY3-XXXX-XXXX-XXXX"""

        # Create keyboard with cancel button
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_restock")]]

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        # Return state to wait for keys
        return WAITING_FOR_KEYS


async def admin_products_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin products menu."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    try:
        await query.edit_message_text(
            "📦 Product Management\n\nSelect an option:",
            reply_markup=create_admin_product_menu_keyboard()
        )
    except Exception:
        # Message is already showing the same content, ignore
        pass


async def admin_manage_categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin category management menu."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    try:
        await query.edit_message_text(
            "📁 Category Management\n\nSelect an option:",
            reply_markup=create_admin_category_menu_keyboard()
        )
    except Exception:
        # Message is already showing the same content, ignore
        pass


async def admin_view_categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of all categories and subcategories."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    with get_db_session() as session:
        categories = session.query(Category).all()

        if not categories:
            await query.edit_message_text("📁 No categories found.")
            return

        message = "📁 Categories & Subcategories:\n\n"

        for cat in categories:
            message += f"📦 {cat.name} (ID: #{cat.id})\n"
            if cat.description:
                message += f"   {cat.description}\n"

            subcategories = session.query(Subcategory).filter_by(category_id=cat.id).all()
            if subcategories:
                for subcat in subcategories:
                    message += f"   └─ {subcat.name} (ID: #{subcat.id})\n"

            message += "\n"

        await query.edit_message_text(message, reply_markup=create_admin_category_menu_keyboard())


async def admin_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin users menu."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    try:
        await query.edit_message_text(
            "👥 User Management\n\nSelect an option:",
            reply_markup=create_admin_user_menu_keyboard()
        )
    except Exception:
        # Message is already showing the same content, ignore
        pass


async def admin_orders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin orders menu."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    try:
        await query.edit_message_text(
            "🛍 Order Management\n\nSelect an option:",
            reply_markup=create_admin_order_menu_keyboard()
        )
    except Exception:
        # Message is already showing the same content, ignore
        pass


async def admin_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin settings menu."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    try:
        await query.edit_message_text(
            "⚙️ Store Settings\n\nSelect an option:",
            reply_markup=create_admin_settings_menu_keyboard()
        )
    except Exception:
        # Message is already showing the same content, ignore
        pass


async def admin_broadcast_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin broadcast menu."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    try:
        await query.edit_message_text(
            "📢 Broadcast Messages\n\nSelect an option:",
            reply_markup=create_admin_broadcast_menu_keyboard()
        )
    except Exception:
        # Message is already showing the same content, ignore
        pass


async def admin_view_users_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show paginated list of users."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    # Get page number from callback data (default to 0)
    page = 0
    if "_page_" in query.data:
        page = int(query.data.split("_page_")[1])

    with get_db_session() as session:
        # Get all users
        all_users = session.query(User).order_by(User.created_at.desc()).all()

        if not all_users:
            await query.edit_message_text(
                "👥 No users found.",
                reply_markup=create_admin_user_menu_keyboard()
            )
            return

        # Pagination settings
        items_per_page = 5
        total_pages = (len(all_users) + items_per_page - 1) // items_per_page
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        users = all_users[start_idx:end_idx]

        # Build user selection keyboard
        keyboard = []
        for user in users:
            status_icon = "🚫" if user.is_banned else "✅"
            username_display = f"@{user.username}" if user.username else f"ID:{user.telegram_id}"
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_icon} {username_display} - {format_price(user.wallet_balance)}",
                    callback_data=f"view_user_{user.id}"
                )
            ])

        # Add pagination buttons if needed
        if total_pages > 1:
            pagination_row = []
            if page > 0:
                pagination_row.append(InlineKeyboardButton("◀️ Previous", callback_data=f"admin_view_users_page_{page-1}"))
            pagination_row.append(InlineKeyboardButton(f"Page {page+1}/{total_pages}", callback_data="noop"))
            if page < total_pages - 1:
                pagination_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"admin_view_users_page_{page+1}"))
            keyboard.append(pagination_row)

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_users")])

        await query.edit_message_text(
            "👥 User List\n\nSelect a user to view details:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def admin_user_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show individual user details with Ban/Unban button."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    # Handle pagination - redirect back to user list
    if "admin_view_users_page_" in query.data:
        return await admin_view_users_callback(update, context)

    # Extract user ID from callback data
    user_id = int(query.data.split("_")[2])

    with get_db_session() as session:
        user = session.query(User).filter_by(id=user_id).first()

        if not user:
            await query.edit_message_text(
                "❌ User not found.",
                reply_markup=create_admin_user_menu_keyboard()
            )
            return

        # Get user statistics
        orders_count = session.query(Order).filter_by(user_id=user.id).count()
        total_spent = session.query(Order).filter_by(user_id=user.id, status='completed').with_entities(
            func.sum(Order.total_amount)
        ).scalar() or 0

        # Format user details
        status = "🚫 Banned" if user.is_banned else "✅ Active"
        username_display = f"@{user.username}" if user.username else "N/A"

        message = f"👤 User Details\n\n"
        message += f"Telegram ID: {user.telegram_id}\n"
        message += f"Username: {username_display}\n"
        message += f"Balance: {format_price(user.wallet_balance)}\n"
        message += f"Status: {status}\n"
        message += f"Total Orders: {orders_count}\n"
        message += f"Total Spent: {format_price(total_spent)}\n"
        message += f"Joined: {user.created_at.strftime('%Y-%m-%d %H:%M')}\n"

        # Build action keyboard
        keyboard = []

        # Ban/Unban button
        if user.is_banned:
            keyboard.append([InlineKeyboardButton("✅ Unban User", callback_data=f"unban_user_{user.id}")])
        else:
            keyboard.append([InlineKeyboardButton("🚫 Ban User", callback_data=f"ban_user_{user.id}")])

        # Back button
        keyboard.append([InlineKeyboardButton("🔙 Back to User List", callback_data="admin_view_users")])

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def admin_ban_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle banning a user."""
    query = update.callback_query
    await query.answer("✅ User banned successfully!", show_alert=True)

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    # Extract user ID from callback data
    user_id = int(query.data.split("_")[2])

    with get_db_session() as session:
        user = session.query(User).filter_by(id=user_id).first()

        if not user:
            await query.edit_message_text(
                "❌ User not found.",
                reply_markup=create_admin_user_menu_keyboard()
            )
            return

        # Store telegram_id before committing
        telegram_id = user.telegram_id

        user.is_banned = True
        session.commit()

        # Clear ban cache for this user
        clear_ban_cache(telegram_id)

        # Refresh user details page - get updated data
        user = session.query(User).filter_by(id=user_id).first()

        # Get user statistics
        orders_count = session.query(Order).filter_by(user_id=user.id).count()
        total_spent = session.query(Order).filter_by(user_id=user.id, status='completed').with_entities(
            func.sum(Order.total_amount)
        ).scalar() or 0

        # Format user details
        status = "🚫 Banned" if user.is_banned else "✅ Active"
        username_display = f"@{user.username}" if user.username else "N/A"

        message = f"👤 User Details\n\n"
        message += f"Telegram ID: {user.telegram_id}\n"
        message += f"Username: {username_display}\n"
        message += f"Balance: {format_price(user.wallet_balance)}\n"
        message += f"Status: {status}\n"
        message += f"Total Orders: {orders_count}\n"
        message += f"Total Spent: {format_price(total_spent)}\n"
        message += f"Joined: {user.created_at.strftime('%Y-%m-%d %H:%M')}\n"

        # Build action keyboard
        keyboard = []

        # Ban/Unban button
        if user.is_banned:
            keyboard.append([InlineKeyboardButton("✅ Unban User", callback_data=f"unban_user_{user.id}")])
        else:
            keyboard.append([InlineKeyboardButton("🚫 Ban User", callback_data=f"ban_user_{user.id}")])

        # Back button
        keyboard.append([InlineKeyboardButton("🔙 Back to User List", callback_data="admin_view_users")])

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def admin_unban_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unbanning a user."""
    query = update.callback_query
    await query.answer("✅ User unbanned successfully!", show_alert=True)

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    # Extract user ID from callback data
    user_id = int(query.data.split("_")[2])

    with get_db_session() as session:
        user = session.query(User).filter_by(id=user_id).first()

        if not user:
            await query.edit_message_text(
                "❌ User not found.",
                reply_markup=create_admin_user_menu_keyboard()
            )
            return

        # Store telegram_id before committing
        telegram_id = user.telegram_id

        user.is_banned = False
        session.commit()

        # Clear ban cache for this user
        clear_ban_cache(telegram_id)

        # Refresh user details page - get updated data
        user = session.query(User).filter_by(id=user_id).first()

        # Get user statistics
        orders_count = session.query(Order).filter_by(user_id=user.id).count()
        total_spent = session.query(Order).filter_by(user_id=user.id, status='completed').with_entities(
            func.sum(Order.total_amount)
        ).scalar() or 0

        # Format user details
        status = "🚫 Banned" if user.is_banned else "✅ Active"
        username_display = f"@{user.username}" if user.username else "N/A"

        message = f"👤 User Details\n\n"
        message += f"Telegram ID: {user.telegram_id}\n"
        message += f"Username: {username_display}\n"
        message += f"Balance: {format_price(user.wallet_balance)}\n"
        message += f"Status: {status}\n"
        message += f"Total Orders: {orders_count}\n"
        message += f"Total Spent: {format_price(total_spent)}\n"
        message += f"Joined: {user.created_at.strftime('%Y-%m-%d %H:%M')}\n"

        # Build action keyboard
        keyboard = []

        # Ban/Unban button
        if user.is_banned:
            keyboard.append([InlineKeyboardButton("✅ Unban User", callback_data=f"unban_user_{user.id}")])
        else:
            keyboard.append([InlineKeyboardButton("🚫 Ban User", callback_data=f"ban_user_{user.id}")])

        # Back button
        keyboard.append([InlineKeyboardButton("🔙 Back to User List", callback_data="admin_view_users")])

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def admin_view_orders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show paginated list of recent orders with management buttons."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    # Get page number from callback data (default to 0)
    page = 0
    if "_page_" in query.data:
        page = int(query.data.split("_page_")[1])

    with get_db_session() as session:
        # Get all orders
        all_orders = session.query(Order).order_by(Order.created_at.desc()).all()

        if not all_orders:
            await query.edit_message_text(
                "🛍 No orders found.",
                reply_markup=create_admin_order_menu_keyboard()
            )
            return

        # Pagination settings
        orders_per_page = 5
        total_pages = (len(all_orders) + orders_per_page - 1) // orders_per_page
        start_idx = page * orders_per_page
        end_idx = start_idx + orders_per_page
        orders = all_orders[start_idx:end_idx]

        # Build message
        message = f"🛍 Recent Orders (Page {page + 1}/{total_pages}):\n\n"

        # Build keyboard with order buttons
        keyboard = []

        for order in orders:
            user = session.query(User).filter_by(id=order.user_id).first()
            username = user.username if user and user.username else f"ID:{user.telegram_id if user else 'Unknown'}"

            # Format status emoji
            status_emoji = {
                OrderStatus.PROCESSING: "⏳",
                OrderStatus.COMPLETED: "✅",
                OrderStatus.CANCELLED: "❌"
            }.get(order.status, "❓")

            # Button text: Order #ID | User | Status | Amount
            button_text = f"{status_emoji} Order #{order.id} | @{username} | {format_price(order.total_amount)}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_order_{order.id}")])

        # Add pagination buttons if needed
        if total_pages > 1:
            pagination_row = []
            if page > 0:
                pagination_row.append(InlineKeyboardButton("◀️ Previous", callback_data=f"admin_view_orders_page_{page-1}"))
            if page < total_pages - 1:
                pagination_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"admin_view_orders_page_{page+1}"))
            if pagination_row:
                keyboard.append(pagination_row)

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_orders")])

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def handle_restock_keys_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file upload for restocking keys."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied.")
        return ConversationHandler.END

    # Get the uploaded file
    document = update.message.document

    if not document:
        await update.message.reply_text("❌ Please upload a text file with keys. Try again or /cancel")
        return WAITING_FOR_KEYS

    # Download file
    file = await context.bot.get_file(document.file_id)
    file_content = await file.download_as_bytearray()

    # Parse keys
    text = file_content.decode('utf-8')
    keys = parse_keys_from_text(text)

    if not keys:
        await update.message.reply_text("❌ No keys found in file. Try again or /cancel")
        return WAITING_FOR_KEYS

    # Get product ID from context (should be set earlier)
    product_id = context.user_data.get('restock_product_id')

    if not product_id:
        await update.message.reply_text("❌ Error: Product not selected. Please start over.")
        return ConversationHandler.END

    # Add keys to product_keys table
    with get_db_session() as session:
        product = session.query(Product).filter_by(id=product_id).first()

        if not product:
            await update.message.reply_text("❌ Product not found.")
            return

        # Insert keys into product_keys table
        added_count = 0
        for key_value in keys:
            product_key = ProductKey(
                product_id=product.id,
                key_value=key_value,
                is_sold=False
            )
            session.add(product_key)
            added_count += 1

        # Update product stock count
        product.stock_count += added_count
        session.commit()

        # Create keyboard with options
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("🔄 Restock More Keys", callback_data="admin_restock_keys")],
            [InlineKeyboardButton("🔙 Back to Product Menu", callback_data="admin_products")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"✅ Successfully added {added_count} keys to {product.name}!\n"
            f"New stock count: {product.stock_count}",
            reply_markup=reply_markup
        )

        # Clear restock_product_id from context
        context.user_data.pop('restock_product_id', None)

        return ConversationHandler.END


async def handle_restock_keys_paste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pasted keys for restocking."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied.")
        return ConversationHandler.END

    # Parse keys from message text
    keys = parse_keys_from_text(update.message.text)

    if not keys:
        await update.message.reply_text("❌ No keys found. Please paste keys (one per line). Try again or /cancel")
        return WAITING_FOR_KEYS

    # Get product ID from context (should be set earlier)
    product_id = context.user_data.get('restock_product_id')

    if not product_id:
        await update.message.reply_text("❌ Error: Product not selected. Please start over.")
        return ConversationHandler.END

    # Add keys to product_keys table
    with get_db_session() as session:
        product = session.query(Product).filter_by(id=product_id).first()

        if not product:
            await update.message.reply_text("❌ Product not found.")
            return

        # Insert keys into product_keys table
        added_count = 0
        for key_value in keys:
            product_key = ProductKey(
                product_id=product.id,
                key_value=key_value,
                is_sold=False
            )
            session.add(product_key)
            added_count += 1

        # Update product stock count
        product.stock_count += added_count
        session.commit()

        # Create keyboard with options
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("🔄 Restock More Keys", callback_data="admin_restock_keys")],
            [InlineKeyboardButton("🔙 Back to Product Menu", callback_data="admin_products")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"✅ Successfully added {added_count} keys to {product.name}!\n"
            f"New stock count: {product.stock_count}",
            reply_markup=reply_markup
        )

        # Clear restock_product_id from context
        context.user_data.pop('restock_product_id', None)

        return ConversationHandler.END


async def handle_welcome_message_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle welcome message update from admin."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied.")
        return

    new_welcome_message = update.message.text

    with get_db_session() as session:
        settings = session.query(Settings).first()

        if not settings:
            settings = Settings()
            session.add(settings)

        settings.welcome_message = new_welcome_message
        settings.updated_at = datetime.utcnow()
        session.commit()

        await update.message.reply_text("✅ Welcome message updated successfully!")


async def handle_logo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle store logo upload from admin."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied.")
        return

    # Get the uploaded photo
    photo = update.message.photo[-1]  # Get highest resolution

    # Download photo
    file = await context.bot.get_file(photo.file_id)
    logo_path = os.path.join(app_settings.LOGOS_DIR, f"store_logo_{int(datetime.utcnow().timestamp())}.jpg")

    # Ensure directory exists
    os.makedirs(app_settings.LOGOS_DIR, exist_ok=True)

    await file.download_to_drive(logo_path)

    # Update settings
    with get_db_session() as session:
        settings = session.query(Settings).first()

        if not settings:
            settings = Settings()
            session.add(settings)

        settings.store_logo_path = logo_path
        settings.updated_at = datetime.utcnow()
        session.commit()

        await update.message.reply_text("✅ Store logo updated successfully!")


async def handle_broadcast_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text-only broadcast to all users."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied.")
        return

    broadcast_text = update.message.text

    with get_db_session() as session:
        # Get all users
        users = session.query(User).filter_by(is_banned=False).all()

        sent_count = 0

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=broadcast_text
                )
                sent_count += 1
            except Exception as e:
                print(f"Failed to send to user {user.telegram_id}: {e}")

        # Save broadcast record
        broadcast = Broadcast(
            message_text=broadcast_text,
            sent_count=sent_count
        )
        session.add(broadcast)
        session.commit()

        await update.message.reply_text(f"✅ Broadcast sent to {sent_count} users!")


async def handle_broadcast_image_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image + text broadcast to all users (as separate messages)."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied.")
        return

    # Get image and caption
    photo = update.message.photo[-1]  # Get highest resolution
    caption_text = update.message.caption or ""

    # Download photo
    file = await context.bot.get_file(photo.file_id)
    image_path = os.path.join(app_settings.ASSETS_DIR, f"broadcast_{int(datetime.utcnow().timestamp())}.jpg")

    os.makedirs(app_settings.ASSETS_DIR, exist_ok=True)
    await file.download_to_drive(image_path)

    with get_db_session() as session:
        # Get all users
        users = session.query(User).filter_by(is_banned=False).all()

        sent_count = 0

        for user in users:
            try:
                # Send image first
                with open(image_path, 'rb') as img:
                    await context.bot.send_photo(
                        chat_id=user.telegram_id,
                        photo=img
                    )

                # Send text as separate message
                if caption_text:
                    await context.bot.send_message(
                        chat_id=user.telegram_id,
                        text=caption_text
                    )

                sent_count += 1
            except Exception as e:
                print(f"Failed to send to user {user.telegram_id}: {e}")

        # Save broadcast record
        broadcast = Broadcast(
            message_text=caption_text,
            image_path=image_path,
            sent_count=sent_count
        )
        session.add(broadcast)
        session.commit()

        await update.message.reply_text(f"✅ Broadcast sent to {sent_count} users!")


async def handle_ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ban/unban user command."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied.")
        return

    # Expected format: telegram_id ban/unban
    try:
        parts = update.message.text.split()
        telegram_id = int(parts[0])
        action = parts[1].lower()

        with get_db_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                await update.message.reply_text("❌ User not found.")
                return

            if action == "ban":
                user.is_banned = True
                session.commit()
                await update.message.reply_text(f"✅ User {telegram_id} has been banned.")
            elif action == "unban":
                user.is_banned = False
                session.commit()
                await update.message.reply_text(f"✅ User {telegram_id} has been unbanned.")
            else:
                await update.message.reply_text("❌ Invalid action. Use 'ban' or 'unban'.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}\n\nFormat: telegram_id ban/unban")


async def handle_cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle order cancellation with wallet refund."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied.")
        return

    try:
        order_id = int(update.message.text)

        with get_db_session() as session:
            order = session.query(Order).filter_by(id=order_id).first()

            if not order:
                await update.message.reply_text("❌ Order not found.")
                return

            if order.status == OrderStatus.CANCELLED:
                await update.message.reply_text("❌ Order is already cancelled.")
                return

            # Refund to wallet
            user = session.query(User).filter_by(id=order.user_id).first()
            user.wallet_balance += order.total_amount

            # Update order status
            order.status = OrderStatus.CANCELLED
            session.commit()

            await update.message.reply_text(
                f"✅ Order #{order_id} cancelled successfully!\n"
                f"💰 Refunded {format_price(order.total_amount)} to user's wallet."
            )

            # Notify user
            await context.bot.send_message(
                chat_id=user.telegram_id,
                text=f"❌ Order #{order_id} has been cancelled by admin.\n"
                     f"💰 {format_price(order.total_amount)} has been refunded to your wallet."
            )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}\n\nFormat: order_id")


async def handle_dispute_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle order dispute status update."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied.")
        return

    try:
        # Format: order_id status (opened/resolved)
        parts = update.message.text.split()
        order_id = int(parts[0])
        status = parts[1].lower()

        with get_db_session() as session:
            order = session.query(Order).filter_by(id=order_id).first()

            if not order:
                await update.message.reply_text("❌ Order not found.")
                return

            if status == "opened":
                order.dispute_status = DisputeStatus.OPENED
            elif status == "resolved":
                order.dispute_status = DisputeStatus.RESOLVED
            else:
                await update.message.reply_text("❌ Invalid status. Use 'opened' or 'resolved'.")
                return

            session.commit()
            await update.message.reply_text(f"✅ Order #{order_id} dispute status updated to: {status.upper()}")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}\n\nFormat: order_id opened/resolved")


async def admin_order_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show individual order details with management buttons."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    # Extract order ID from callback data
    order_id = int(query.data.split("_")[2])

    with get_db_session() as session:
        order = session.query(Order).filter_by(id=order_id).first()

        if not order:
            await query.edit_message_text(
                "❌ Order not found.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_view_orders")]])
            )
            return

        # Get user and order items
        user = session.query(User).filter_by(id=order.user_id).first()
        order_items = session.query(OrderItem).filter_by(order_id=order.id).all()

        # Format status emoji
        status_emoji = {
            OrderStatus.PROCESSING: "⏳",
            OrderStatus.COMPLETED: "✅",
            OrderStatus.CANCELLED: "❌"
        }.get(order.status, "❓")

        # Build message
        username = user.username if user and user.username else f"ID:{user.telegram_id if user else 'Unknown'}"
        message = f"📋 Order Details\n\n"
        message += f"Order ID: #{order.id}\n"
        message += f"Status: {status_emoji} {order.status.value}\n"
        message += f"User: @{username} ({user.telegram_id if user else 'Unknown'})\n"
        message += f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        message += f"Total: {format_price(order.total_amount)}\n\n"

        message += "📦 Items:\n"
        for item in order_items:
            product = session.query(Product).filter_by(id=item.product_id).first()
            product_name = product.name if product else "Unknown Product"
            message += f"• {product_name} x{item.quantity} = {format_price(item.price * item.quantity)}\n"

            # Add delivered assets (keys or download links)
            if item.delivered_asset:
                if product and product.product_type == ProductType.KEY:
                    message += f"  🔐 Keys:\n{item.delivered_asset}\n"
                elif product and product.product_type == ProductType.FILE:
                    message += f"  🔗 Download: {item.delivered_asset}\n"
                message += "\n"

        # Build keyboard with management buttons
        keyboard = []

        # Status-specific actions
        if order.status == OrderStatus.PROCESSING:
            keyboard.append([InlineKeyboardButton("✅ Mark as Completed", callback_data=f"complete_order_{order.id}")])
            keyboard.append([InlineKeyboardButton("❌ Cancel Order", callback_data=f"cancel_order_{order.id}")])
        elif order.status == OrderStatus.CANCELLED:
            keyboard.append([InlineKeyboardButton("🔄 Reactivate Order", callback_data=f"reactivate_order_{order.id}")])

        # Navigation buttons
        keyboard.append([InlineKeyboardButton("🔙 Back to Orders", callback_data="admin_view_orders")])

        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def admin_complete_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark an order as completed."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    order_id = int(query.data.split("_")[2])

    with get_db_session() as session:
        order = session.query(Order).filter_by(id=order_id).first()

        if not order:
            await query.edit_message_text("❌ Order not found.")
            return

        order.status = OrderStatus.COMPLETED
        session.commit()

        await query.answer("✅ Order marked as completed!", show_alert=True)

        # Refresh order details
        await admin_order_detail_callback(update, context)


async def admin_confirm_order_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of pending transactions for manual confirmation."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    with get_db_session() as session:
        from database import Transaction, TransactionStatus

        # Get all pending transactions
        transactions = session.query(Transaction).filter_by(status=TransactionStatus.PENDING).order_by(Transaction.created_at.desc()).all()

        if not transactions:
            keyboard = [[InlineKeyboardButton("🔙 Back to Orders", callback_data="admin_orders")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "✅ No pending payments to confirm.",
                reply_markup=reply_markup
            )
            return

        # Build keyboard with transaction buttons
        keyboard = []
        for txn in transactions:
            user = session.query(User).filter_by(id=txn.user_id).first()
            username = user.username if user and user.username else f"ID:{user.telegram_id if user else 'Unknown'}"

            payment_method = txn.payment_method.value.replace('_', ' ').title()

            button_text = f"⏳ Txn #{txn.id} | @{username} | {format_price(txn.amount)} | {payment_method}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"confirm_payment_{txn.id}")])

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back to Orders", callback_data="admin_orders")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = f"✅ Manual Payment Confirmation ({len(transactions)} pending)\n\nSelect a transaction to confirm:"

        await query.edit_message_text(message, reply_markup=reply_markup)


async def admin_cancel_order_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of pending transactions for cancellation."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    with get_db_session() as session:
        from database import Transaction, TransactionStatus

        # Get all pending transactions
        transactions = session.query(Transaction).filter_by(status=TransactionStatus.PENDING).order_by(Transaction.created_at.desc()).all()

        if not transactions:
            keyboard = [[InlineKeyboardButton("🔙 Back to Orders", callback_data="admin_orders")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "✅ No pending payments to cancel.",
                reply_markup=reply_markup
            )
            return

        # Build keyboard with transaction buttons
        keyboard = []
        for txn in transactions:
            user = session.query(User).filter_by(id=txn.user_id).first()
            username = user.username if user and user.username else f"ID:{user.telegram_id if user else 'Unknown'}"

            payment_method = txn.payment_method.value.replace('_', ' ').title()
            button_text = f"⏳ Txn #{txn.id} | @{username} | {format_price(txn.amount)} | {payment_method}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"cancel_payment_{txn.id}")])

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back to Orders", callback_data="admin_orders")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = f"❌ Cancel Payments ({len(transactions)} pending)\n\nSelect a transaction to cancel:"

        await query.edit_message_text(message, reply_markup=reply_markup)


async def admin_confirm_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually confirm a pending payment transaction."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    txn_id = int(query.data.split("_")[2])

    with get_db_session() as session:
        from database import Transaction, TransactionStatus
        from datetime import datetime

        txn = session.query(Transaction).filter_by(id=txn_id).first()

        if not txn:
            await query.edit_message_text("❌ Transaction not found.")
            return

        if txn.status != TransactionStatus.PENDING:
            await query.answer(f"⚠️ Transaction is already {txn.status.value}", show_alert=True)
            return

        # Add funds to user's wallet
        user = session.query(User).filter_by(id=txn.user_id).first()
        if user:
            user.wallet_balance += txn.amount

        # Mark transaction as completed
        txn.status = TransactionStatus.COMPLETED
        txn.completed_at = datetime.utcnow()
        session.commit()

        # Get details before session closes
        user_telegram_id = user.telegram_id if user else None
        amount = txn.amount
        new_balance = user.wallet_balance if user else 0

        await query.answer(f"✅ Payment confirmed! {format_price(amount)} added to user's wallet.", show_alert=True)

        # Notify user
        if user_telegram_id:
            try:
                await context.bot.send_message(
                    chat_id=user_telegram_id,
                    text=f"✅ Payment Confirmed!\n\n💰 Amount: {format_price(amount)}\n💵 New Balance: {format_price(new_balance)}"
                )
            except:
                pass

        # Go back to payment confirmation menu
        await admin_confirm_order_menu(update, context)


async def admin_cancel_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel a pending payment transaction."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    txn_id = int(query.data.split("_")[2])

    with get_db_session() as session:
        from database import Transaction, TransactionStatus

        txn = session.query(Transaction).filter_by(id=txn_id).first()

        if not txn:
            await query.edit_message_text("❌ Transaction not found.")
            return

        if txn.status != TransactionStatus.PENDING:
            await query.answer(f"⚠️ Transaction is already {txn.status.value}", show_alert=True)
            return

        # Mark transaction as failed
        txn.status = TransactionStatus.FAILED
        session.commit()

        # Get details before session closes
        user = session.query(User).filter_by(id=txn.user_id).first()
        user_telegram_id = user.telegram_id if user else None
        amount = txn.amount

        await query.answer(f"✅ Payment cancelled!", show_alert=True)

        # Notify user
        if user_telegram_id:
            try:
                await context.bot.send_message(
                    chat_id=user_telegram_id,
                    text=f"❌ Payment Cancelled\n\n💰 Amount: {format_price(amount)}\n\nYour payment was not confirmed. Please contact support if you believe this is an error."
                )
            except:
                pass

        # Go back to payment cancellation menu
        await admin_cancel_order_menu(update, context)


async def admin_cancel_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel an order and refund the user."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return

    order_id = int(query.data.split("_")[2])

    with get_db_session() as session:
        order = session.query(Order).filter_by(id=order_id).first()

        if not order:
            await query.edit_message_text("❌ Order not found.")
            return

        # Refund user
        user = session.query(User).filter_by(id=order.user_id).first()
        if user:
            user.wallet_balance += order.total_amount

        # Mark order as cancelled
        order.status = OrderStatus.CANCELLED
        session.commit()

        await query.answer(f"✅ Order cancelled and {format_price(order.total_amount)} refunded!", show_alert=True)

        # Notify user
        if user:
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"❌ Order #{order.id} has been cancelled by admin.\n💰 Refund: {format_price(order.total_amount)}"
                )
            except:
                pass

        # Refresh order details
        await admin_order_detail_callback(update, context)




async def cancel_restock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the restock keys conversation."""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            "❌ Restock cancelled.",
            reply_markup=create_admin_product_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Restock cancelled.",
            reply_markup=create_admin_product_menu_keyboard()
        )

    # Clear restock_product_id from context
    context.user_data.pop('restock_product_id', None)

    return ConversationHandler.END
