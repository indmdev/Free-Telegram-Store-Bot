"""User-facing command and callback handlers."""

import os
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_db_session, User, Category, Subcategory, Product, Order, OrderItem, Settings, ProductType, OrderStatus, DisputeStatus
from utils import (
    get_or_create_user, format_price, format_datetime, create_main_menu_keyboard,
    create_pagination_keyboard, create_product_detail_keyboard,
    create_support_keyboard, check_user_banned,
    paginate_items, format_product_display, build_availability_text,
    create_back_support_keyboard
)
from config.settings import settings as app_settings


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show welcome message with wallet balance."""
    user = update.effective_user
    telegram_id = user.id
    username = user.username

    # Check if user is banned
    if check_user_banned(telegram_id):
        await update.message.reply_text("⛔ You have been banned from using this bot.")
        return

    # Get or create user and fetch settings in same session
    with get_db_session() as session:
        # Get or create user
        db_user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not db_user:
            db_user = User(telegram_id=telegram_id, username=username)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)

        wallet_balance = db_user.wallet_balance

        # Get store settings
        store_settings = session.query(Settings).first()
        welcome_msg = store_settings.welcome_message if store_settings else "Welcome to our Digital Products Store!"
        logo_path = store_settings.store_logo_path if store_settings else None

    # Send logo if available
    if logo_path and os.path.exists(logo_path):
        with open(logo_path, 'rb') as logo:
            await update.message.reply_photo(photo=logo)

    # Send welcome message with wallet balance
    message = f"{welcome_msg}\n\n💰 Your Wallet Balance: {format_price(wallet_balance)}"

    await update.message.reply_text(
        message,
        reply_markup=create_main_menu_keyboard()
    )


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu callback - return to main menu."""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    # Check if user is banned
    if check_user_banned(user_id):
        await query.edit_message_text("⛔ You have been banned from using this bot.")
        return

    with get_db_session() as session:
        # Get user
        db_user = session.query(User).filter_by(telegram_id=user_id).first()
        if not db_user:
            db_user = User(telegram_id=user_id)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)

        wallet_balance = db_user.wallet_balance

        # Get store settings
        store_settings = session.query(Settings).first()
        welcome_msg = store_settings.welcome_message if store_settings else "Welcome to our Digital Products Store!"

    message = f"{welcome_msg}\n\n💰 Your Wallet Balance: {format_price(wallet_balance)}"

    await query.edit_message_text(
        message,
        reply_markup=create_main_menu_keyboard()
    )


async def products_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle products button - show category list."""
    query = update.callback_query
    await query.answer()

    # Check if user is banned
    if check_user_banned(update.effective_user.id):
        await query.edit_message_text("⛔ You have been banned from using this bot.")
        return

    # If coming from a photo message, delete it and create new text message
    if query.message.photo:
        await query.message.delete()
        message = await query.message.reply_text("Loading...")

        # Create mock query object
        class MockQuery:
            def __init__(self, message):
                self.message = message
            async def edit_message_text(self, text, reply_markup=None):
                await self.message.edit_text(text, reply_markup=reply_markup)

        query = MockQuery(message)

    # Extract page number from callback data
    callback_data = query.data if hasattr(query, 'data') else "products"
    page = 0
    if "_page_" in callback_data:
        page = int(callback_data.split("_page_")[1])

    with get_db_session() as session:
        categories = session.query(Category).all()

        if not categories:
            await query.edit_message_text(
                "📦 No categories available yet.",
                reply_markup=create_back_support_keyboard()
            )
            return

        # Paginate categories
        page_info = paginate_items(categories, page, page_size=5)

        # Create category buttons
        category_buttons = [
            [InlineKeyboardButton(cat.name, callback_data=f"category_{cat.id}")]
            for cat in page_info['items']
        ]

        keyboard = create_pagination_keyboard(
            category_buttons,
            page_info['page'],
            page_info['total_pages'],
            "products"
        )

        text = "📦 Select a Category for the product you need:"
        if page_info['total_pages'] > 1:
            text += f"\n\nPage {page_info['page'] + 1} of {page_info['total_pages']}"

        await query.edit_message_text(text, reply_markup=keyboard)


async def product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product callback."""
    await product_detail_callback(update, context)


async def subcategory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subcategory selection."""
    query = update.callback_query
    await query.answer()

    # Check if user is banned
    if check_user_banned(update.effective_user.id):
        await query.edit_message_text("⛔ You have been banned from using this bot.")
        return

    subcategory_id = int(query.data.split("_")[1])

    # If coming from a photo message (product detail with image), delete and send new message
    if query.message.photo:
        await query.message.delete()
        # Create a new text message for products list
        message = await query.message.reply_text("Loading products...")
        # Now we need to pass this message to show_products_list
        # We'll use a workaround by creating a mock query object
        class MockQuery:
            def __init__(self, message):
                self.message = message
            async def edit_message_text(self, text, reply_markup=None):
                await self.message.edit_text(text, reply_markup=reply_markup)

        mock_query = MockQuery(message)
        await show_products_list(mock_query, subcategory_id=subcategory_id, context=context)
    else:
        await show_products_list(query, subcategory_id=subcategory_id, context=context)


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection - show subcategories or products."""
    query = update.callback_query
    await query.answer()

    # Check if user is banned
    if check_user_banned(update.effective_user.id):
        await query.edit_message_text("⛔ You have been banned from using this bot.")
        return

    callback_data = query.data
    category_id = int(callback_data.split("_")[1])

    # If coming from a photo message, delete it and create new text message
    if query.message.photo:
        await query.message.delete()
        message = await query.message.reply_text("Loading...")

        # Create mock query object
        class MockQuery:
            def __init__(self, message):
                self.message = message
            async def edit_message_text(self, text, reply_markup=None):
                await self.message.edit_text(text, reply_markup=reply_markup)

        query = MockQuery(message)

    with get_db_session() as session:
        category = session.query(Category).filter_by(id=category_id).first()

        if not category:
            await query.edit_message_text("❌ Category not found.")
            return

        # Check if category has subcategories
        subcategories = session.query(Subcategory).filter_by(category_id=category_id).all()

        if subcategories:
            # Show subcategories
            subcat_buttons = [
                [InlineKeyboardButton(subcat.name, callback_data=f"subcategory_{subcat.id}")]
                for subcat in subcategories[:5]
            ]

            # Create keyboard with back to products
            from telegram import InlineKeyboardMarkup
            keyboard = subcat_buttons + [[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_products"),
                InlineKeyboardButton("☎️ Support", callback_data="support")
            ]]

            await query.edit_message_text(
                f"📦 Select the product you need from {category.name}:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # Show products directly
            await show_products_list(query, category_id=category_id, context=context)


async def show_products_list(query, category_id=None, subcategory_id=None, page=0, context=None):
    """Show list of products for a category or subcategory."""
    with get_db_session() as session:
        query_filter = Product.is_active == True

        if category_id:
            products = session.query(Product).filter(
                Product.category_id == category_id,
                Product.subcategory_id == None,
                query_filter
            ).all()
        elif subcategory_id:
            products = session.query(Product).filter(
                Product.subcategory_id == subcategory_id,
                query_filter
            ).all()
        else:
            products = session.query(Product).filter(query_filter).all()

        if not products:
            await query.edit_message_text(
                "📦 No products available in this category.",
                reply_markup=create_back_support_keyboard()
            )
            return

        # Paginate products
        page_info = paginate_items(products, page, page_size=5)

        # Create product buttons
        product_buttons = [
            [InlineKeyboardButton(
                f"{prod.name} | {format_price(prod.price)} | Available: {prod.stock_count}",
                callback_data=f"product_{prod.id}"
            )]
            for prod in page_info['items']
        ]

        # Add pagination if needed
        from telegram import InlineKeyboardMarkup
        keyboard = product_buttons.copy()
        if page_info['total_pages'] > 1:
            pagination_row = []
            if page > 0:
                pagination_row.append(InlineKeyboardButton("◀️ Previous", callback_data=f"products_page_{page-1}"))
            if page < page_info['total_pages'] - 1:
                pagination_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"products_page_{page+1}"))
            if pagination_row:
                keyboard.append(pagination_row)

        # Determine back button based on what we're showing
        if subcategory_id:
            # Get the subcategory to find its parent category
            subcategory = session.query(Subcategory).filter_by(id=subcategory_id).first()
            if subcategory and subcategory.category_id:
                # Back to category (which will show subcategories)
                back_data = f"category_{subcategory.category_id}"
            else:
                back_data = "back_to_products"
        elif category_id:
            # Back to products (category list)
            back_data = "back_to_products"
        else:
            back_data = "back_to_products"

        keyboard.append([
            InlineKeyboardButton("🔙 Back", callback_data=back_data),
            InlineKeyboardButton("☎️ Support", callback_data="support")
        ])

        text = "📦 Select the product you need:"
        if page_info['total_pages'] > 1:
            text += f"\n\nPage {page_info['page'] + 1} of {page_info['total_pages']}"

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def product_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product selection - show product details."""
    query = update.callback_query
    await query.answer()

    # Check if user is banned
    if check_user_banned(update.effective_user.id):
        await query.edit_message_text("⛔ You have been banned from using this bot.")
        return

    product_id = int(query.data.split("_")[1])

    with get_db_session() as session:
        product = session.query(Product).filter_by(id=product_id).first()

        if not product:
            await query.edit_message_text("❌ Product not found.")
            return

        # Determine back navigation based on product's category/subcategory
        if product.subcategory_id:
            # Product belongs to a subcategory - go back to subcategory list
            back_callback = f"subcategory_{product.subcategory_id}"
        elif product.category_id:
            # Product belongs to a category - go back to category
            back_callback = f"category_{product.category_id}"
        else:
            # Fallback to products list
            back_callback = "back_to_products"

        # Format product details
        details = format_product_display(product, include_description=True)

        # Send product image if available
        if product.image_path and os.path.exists(product.image_path):
            with open(product.image_path, 'rb') as image:
                await query.message.reply_photo(
                    photo=image,
                    caption=details,
                    reply_markup=create_product_detail_keyboard(product_id, back_callback)
                )
            await query.message.delete()
        else:
            await query.edit_message_text(
                details,
                reply_markup=create_product_detail_keyboard(product_id, back_callback)
            )


async def availability_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle availability button - show all available products."""
    query = update.callback_query
    await query.answer()

    # Check if user is banned
    if check_user_banned(update.effective_user.id):
        await query.edit_message_text("⛔ You have been banned from using this bot.")
        return

    with get_db_session() as session:
        categories = session.query(Category).all()
        products_by_category = {}

        for category in categories:
            products = session.query(Product).filter_by(
                category_id=category.id,
                is_active=True
            ).limit(15).all()

            if products:
                products_by_category[category.name] = products

        if not products_by_category:
            await query.edit_message_text(
                "📦 No products available yet.",
                reply_markup=create_back_support_keyboard()
            )
            return

        text = build_availability_text(products_by_category)

        await query.edit_message_text(
            text,
            reply_markup=create_back_support_keyboard()
        )


async def support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle support button - show support page."""
    query = update.callback_query
    await query.answer()

    # Check if user is banned
    if check_user_banned(update.effective_user.id):
        await query.edit_message_text("⛔ You have been banned from using this bot.")
        return

    with get_db_session() as session:
        store_settings = session.query(Settings).first()

        support_username = store_settings.support_username if store_settings else ""
        channel_username = store_settings.channel_username if store_settings else ""

        message = "☎️ My Shop is Open 24/7"

        await query.edit_message_text(
            message,
            reply_markup=create_support_keyboard(support_username, channel_username)
        )


async def order_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle order history button - show user's order history as clickable list."""
    query = update.callback_query
    await query.answer()

    # Check if user is banned
    if check_user_banned(update.effective_user.id):
        await query.edit_message_text("⛔ You have been banned from using this bot.")
        return

    user_id = update.effective_user.id

    with get_db_session() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()

        if not user:
            await query.edit_message_text("❌ User not found.")
            return

        orders = session.query(Order).filter_by(user_id=user.id).order_by(Order.created_at.desc()).limit(10).all()

        if not orders:
            await query.edit_message_text(
                "🛍 No orders yet.",
                reply_markup=create_back_support_keyboard()
            )
            return

        # Build keyboard with order buttons
        keyboard = []
        for order in orders:
            status_emoji = {
                OrderStatus.PROCESSING: "⏳",
                OrderStatus.COMPLETED: "✅",
                OrderStatus.CANCELLED: "❌"
            }.get(order.status, "❓")

            dispute_indicator = ""
            if order.dispute_status == DisputeStatus.OPENED:
                dispute_indicator = " 🚨"
            elif order.dispute_status == DisputeStatus.RESOLVED:
                dispute_indicator = " ✔️"

            button_text = f"{status_emoji} Order #{order.id} | {format_price(order.total_amount)}{dispute_indicator}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"user_order_detail_{order.id}")])

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🛍 Your Order History\n\nClick on an order to view details:",
            reply_markup=reply_markup
        )


async def user_order_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show order detail view with dispute button for user."""
    query = update.callback_query
    await query.answer()

    # Check if user is banned
    if check_user_banned(update.effective_user.id):
        await query.edit_message_text("⛔ You have been banned from using this bot.")
        return

    # Extract order_id from callback data
    order_id = int(query.data.split("_")[3])
    user_id = update.effective_user.id

    with get_db_session() as session:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            await query.edit_message_text("❌ User not found.")
            return

        order = session.query(Order).filter_by(id=order_id, user_id=user.id).first()
        if not order:
            await query.edit_message_text("❌ Order not found.")
            return

        order_items = session.query(OrderItem).filter_by(order_id=order.id).all()

        # Build order details message
        items_text = ""
        for item in order_items:
            items_text += f"  📦 {item.product.name} (x{item.quantity}) - {format_price(item.price * item.quantity)}\n"

            # Add delivered assets (keys or download links)
            if item.delivered_asset:
                if item.product.product_type == ProductType.KEY:
                    items_text += f"  🔐 Keys:\n{item.delivered_asset}\n"
                elif item.product.product_type == ProductType.FILE:
                    items_text += f"  🔗 Download: {item.delivered_asset}\n"
            items_text += "\n"

        status_emoji = {
            OrderStatus.PROCESSING: "⏳",
            OrderStatus.COMPLETED: "✅",
            OrderStatus.CANCELLED: "❌"
        }.get(order.status, "❓")

        dispute_text = ""
        if order.dispute_status == DisputeStatus.OPENED:
            dispute_text = "\n🚨 Dispute Status: OPEN - Admin will review soon"
        elif order.dispute_status == DisputeStatus.RESOLVED:
            dispute_text = "\n✔️ Dispute Status: RESOLVED"

        message = f"""🛍 Order Details

🔸 Order #{order.id}
{status_emoji} Status: {order.status.value}
💰 Total Amount: {format_price(order.total_amount)}
📅 Date: {format_datetime(order.created_at)}

📦 Items:
{items_text}{dispute_text}"""

        # Build keyboard based on order status
        keyboard = []

        # Add dispute button if no dispute is open/resolved
        if order.dispute_status == DisputeStatus.NIL:
            keyboard.append([InlineKeyboardButton("🚨 Open Dispute", callback_data=f"open_dispute_{order.id}")])

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back to Orders", callback_data="order_history")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(message, reply_markup=reply_markup)


async def back_to_products_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to products - show category list."""
    # Just redirect to products_callback
    await products_callback(update, context)
