"""Admin conversation handlers for multi-step workflows."""

import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import (
    get_db_session, Category, Subcategory, Product, ProductType, Settings
)
from utils import is_admin, format_price, create_admin_product_menu_keyboard, create_admin_category_menu_keyboard
from config.settings import settings as app_settings

# Conversation states for product creation
PRODUCT_NAME, PRODUCT_DESC, PRODUCT_PRICE, PRODUCT_TYPE, PRODUCT_CATEGORY, PRODUCT_SUBCATEGORY, PRODUCT_IMAGE, PRODUCT_DOWNLOAD_LINK, PRODUCT_KEYS = range(9)

# Conversation states for category management
CATEGORY_NAME, CATEGORY_DESC = range(2)

# Conversation states for subcategory management
SUBCATEGORY_CATEGORY, SUBCATEGORY_NAME = range(2)

# Conversation states for product edit
EDIT_SELECT_PRODUCT, EDIT_SELECT_FIELD, EDIT_NEW_VALUE, EDIT_IMAGE_VALUE = range(4)

# Conversation states for category edit
EDIT_CATEGORY_SELECT, EDIT_CATEGORY_FIELD, EDIT_CATEGORY_VALUE = range(3)

# Conversation states for subcategory edit
EDIT_SUBCATEGORY_SELECT, EDIT_SUBCATEGORY_FIELD, EDIT_SUBCATEGORY_VALUE = range(3)

# Conversation states for settings
SETTING_VALUE = range(1)

# Conversation states for broadcast
BROADCAST_TEXT, BROADCAST_IMAGE = range(2)

# Conversation states for welcome message and store logo
WELCOME_MESSAGE, STORE_LOGO = range(2)


# ==================== PRODUCT CREATION FLOW ====================

async def create_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start product creation flow."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    # Create cancel button
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_product")]]

    await query.edit_message_text(
        "📦 Create New Product\n\nPlease enter the product name:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PRODUCT_NAME


async def product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product name input."""
    context.user_data['product_name'] = update.message.text

    # Create cancel button
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_product")]]

    await update.message.reply_text(
        "📝 Please enter the product description:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PRODUCT_DESC


async def product_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product description input."""
    context.user_data['product_desc'] = update.message.text

    # Create cancel button
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_product")]]

    await update.message.reply_text(
        "💰 Please enter the product price (USD):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return PRODUCT_PRICE


async def product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product price input."""
    # Create cancel button for error messages
    cancel_keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_product")]]

    try:
        price = float(update.message.text)
        if price <= 0:
            await update.message.reply_text(
                "❌ Price must be greater than 0. Please enter a valid price:",
                reply_markup=InlineKeyboardMarkup(cancel_keyboard)
            )
            return PRODUCT_PRICE

        context.user_data['product_price'] = price

        # Ask for product type
        keyboard = [
            [InlineKeyboardButton("🔑 Software Key", callback_data="type_key")],
            [InlineKeyboardButton("📁 Downloadable File", callback_data="type_file")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_product")]
        ]
        await update.message.reply_text(
            "📦 Select product type:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return PRODUCT_TYPE

    except ValueError:
        await update.message.reply_text(
            "❌ Invalid price. Please enter a number:",
            reply_markup=InlineKeyboardMarkup(cancel_keyboard)
        )
        return PRODUCT_PRICE


async def product_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product type selection."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_product":
        await query.edit_message_text(
            "❌ Product creation cancelled.",
            reply_markup=create_admin_product_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END

    product_type = ProductType.KEY if query.data == "type_key" else ProductType.FILE
    context.user_data['product_type'] = product_type

    # Get categories and show selection
    with get_db_session() as session:
        categories = session.query(Category).all()

        if not categories:
            await query.edit_message_text(
                "❌ No categories available. Please create a category first.",
                reply_markup=create_admin_product_menu_keyboard()
            )
            context.user_data.clear()
            return ConversationHandler.END

        keyboard = []
        for cat in categories:
            keyboard.append([InlineKeyboardButton(cat.name, callback_data=f"cat_{cat.id}")])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_product")])

        await query.edit_message_text(
            "📁 Select a category for this product:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return PRODUCT_CATEGORY


async def product_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product category selection."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_product":
        await query.edit_message_text(
            "❌ Product creation cancelled.",
            reply_markup=create_admin_product_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END

    category_id = int(query.data.split("_")[1])
    context.user_data['product_category'] = category_id

    # Check if category has subcategories
    with get_db_session() as session:
        subcategories = session.query(Subcategory).filter_by(category_id=category_id).all()

        if subcategories:
            keyboard = [[InlineKeyboardButton("⏭ Skip (No Subcategory)", callback_data="subcat_skip")]]
            for subcat in subcategories:
                keyboard.append([InlineKeyboardButton(subcat.name, callback_data=f"subcat_{subcat.id}")])
            keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_product")])

            await query.edit_message_text(
                "📂 Select a subcategory (optional):",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return PRODUCT_SUBCATEGORY
        else:
            # No subcategories, skip to image
            context.user_data['product_subcategory'] = None

            # Create cancel button
            cancel_keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_product")]]

            await query.edit_message_text(
                "🖼 Send a product image (optional) or type 'skip' to skip:",
                reply_markup=InlineKeyboardMarkup(cancel_keyboard)
            )
            return PRODUCT_IMAGE


async def product_subcategory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product subcategory selection."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_product":
        await query.edit_message_text(
            "❌ Product creation cancelled.",
            reply_markup=create_admin_product_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "subcat_skip":
        context.user_data['product_subcategory'] = None
    else:
        subcategory_id = int(query.data.split("_")[1])
        context.user_data['product_subcategory'] = subcategory_id

    # Create cancel button
    cancel_keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_product")]]

    await query.edit_message_text(
        "🖼 Send a product image (optional) or type 'skip' to skip:",
        reply_markup=InlineKeyboardMarkup(cancel_keyboard)
    )
    return PRODUCT_IMAGE


async def product_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product image upload."""
    # Create cancel button
    cancel_keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_product")]]

    if update.message.text and update.message.text.lower() == 'skip':
        context.user_data['product_image'] = None

        # Check if it's a file type product
        if context.user_data['product_type'] == ProductType.FILE:
            await update.message.reply_text(
                "🔗 Please enter the download link for this file product:",
                reply_markup=InlineKeyboardMarkup(cancel_keyboard)
            )
            return PRODUCT_DOWNLOAD_LINK
        else:
            # Ask for keys for KEY products
            await update.message.reply_text(
                "🔑 Please paste the product keys (one per line) or upload a .txt file:\n\n"
                "Example:\n"
                "KEY1-XXXX-XXXX-XXXX\n"
                "KEY2-XXXX-XXXX-XXXX\n"
                "KEY3-XXXX-XXXX-XXXX\n\n"
                "Or type 'skip' to add keys later.",
                reply_markup=InlineKeyboardMarkup(cancel_keyboard)
            )
            return PRODUCT_KEYS

    elif update.message.photo:
        # Download and save image
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_path = os.path.join(
            app_settings.PRODUCTS_DIR,
            f"product_{int(datetime.utcnow().timestamp())}.jpg"
        )
        os.makedirs(app_settings.PRODUCTS_DIR, exist_ok=True)
        await file.download_to_drive(image_path)

        context.user_data['product_image'] = image_path

        # Check if it's a file type product
        if context.user_data['product_type'] == ProductType.FILE:
            await update.message.reply_text(
                "🔗 Please enter the download link for this file product:",
                reply_markup=InlineKeyboardMarkup(cancel_keyboard)
            )
            return PRODUCT_DOWNLOAD_LINK
        else:
            # Ask for keys for KEY products
            await update.message.reply_text(
                "🔑 Please paste the product keys (one per line) or upload a .txt file:\n\n"
                "Example:\n"
                "KEY1-XXXX-XXXX-XXXX\n"
                "KEY2-XXXX-XXXX-XXXX\n"
                "KEY3-XXXX-XXXX-XXXX\n\n"
                "Or type 'skip' to add keys later.",
                reply_markup=InlineKeyboardMarkup(cancel_keyboard)
            )
            return PRODUCT_KEYS
    else:
        await update.message.reply_text(
            "❌ Please send an image or type 'skip':",
            reply_markup=InlineKeyboardMarkup(cancel_keyboard)
        )
        return PRODUCT_IMAGE


async def product_download_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle download link for file products."""
    context.user_data['product_download_link'] = update.message.text

    # Create product
    await create_product_final(update, context)
    return ConversationHandler.END


async def product_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product keys input for KEY products (text or file upload)."""
    from database import ProductKey
    from utils import parse_keys_from_text

    # Create cancel button for error messages
    cancel_keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_product")]]

    # Handle file upload
    if update.message.document:
        try:
            # Download file
            document = update.message.document
            file = await context.bot.get_file(document.file_id)
            file_content = await file.download_as_bytearray()

            # Parse keys from file
            text = file_content.decode('utf-8')
            keys = parse_keys_from_text(text)

            if not keys:
                await update.message.reply_text(
                    "❌ No valid keys found in file. Try again, paste keys directly, or type 'skip':",
                    reply_markup=InlineKeyboardMarkup(cancel_keyboard)
                )
                return PRODUCT_KEYS

            # Store keys temporarily
            context.user_data['product_keys'] = keys

            # Create product with keys
            await create_product_final(update, context)
            return ConversationHandler.END

        except Exception as e:
            await update.message.reply_text(
                f"❌ Error reading file: {str(e)}\n\nTry again, paste keys directly, or type 'skip':",
                reply_markup=InlineKeyboardMarkup(cancel_keyboard)
            )
            return PRODUCT_KEYS

    # Handle text input
    elif update.message.text:
        if update.message.text.lower() == 'skip':
            # Skip adding keys for now
            context.user_data['product_keys'] = []
            await create_product_final(update, context)
            return ConversationHandler.END

        # Parse keys from pasted text
        keys = parse_keys_from_text(update.message.text)

        if not keys:
            await update.message.reply_text(
                "❌ No valid keys found. Please paste keys (one per line), upload a .txt file, or type 'skip':",
                reply_markup=InlineKeyboardMarkup(cancel_keyboard)
            )
            return PRODUCT_KEYS

        # Store keys temporarily
        context.user_data['product_keys'] = keys

        # Create product with keys
        await create_product_final(update, context)
        return ConversationHandler.END

    else:
        await update.message.reply_text(
            "❌ Please paste keys, upload a .txt file, or type 'skip':",
            reply_markup=InlineKeyboardMarkup(cancel_keyboard)
        )
        return PRODUCT_KEYS


async def create_product_final(update, context):
    """Create the product in the database."""
    from database import ProductKey

    with get_db_session() as session:
        # Get keys if provided
        product_keys = context.user_data.get('product_keys', [])
        stock_count = len(product_keys) if product_keys else 0

        # For file products, set stock to 999999 (unlimited)
        if context.user_data['product_type'] == ProductType.FILE:
            stock_count = 999999

        product = Product(
            name=context.user_data['product_name'],
            description=context.user_data['product_desc'],
            price=context.user_data['product_price'],
            product_type=context.user_data['product_type'],
            category_id=context.user_data['product_category'],
            subcategory_id=context.user_data.get('product_subcategory'),
            image_path=context.user_data.get('product_image'),
            download_link=context.user_data.get('product_download_link'),
            stock_count=stock_count,
            is_active=True
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        # Add keys to product_keys table if provided
        keys_added = 0
        if product_keys and context.user_data['product_type'] == ProductType.KEY:
            for key_value in product_keys:
                product_key = ProductKey(
                    product_id=product.id,
                    key_value=key_value,
                    is_sold=False
                )
                session.add(product_key)
                keys_added += 1
            session.commit()

        # Build success message
        message = f"""✅ Product Created Successfully!

📦 Name: {product.name}
💰 Price: {format_price(product.price)}
📝 Type: {product.product_type.value}
📁 Category ID: {product.category_id}

Product ID: #{product.id}"""

        if keys_added > 0:
            message += f"\n🔑 Keys Added: {keys_added}"
        elif context.user_data['product_type'] == ProductType.KEY:
            message += "\n\n⚠️ No keys added. Use the Restock Keys option to add inventory."

        # Create keyboard with options
        keyboard = [
            [InlineKeyboardButton("➕ Create Another Product", callback_data="admin_create_product")],
            [InlineKeyboardButton("🔙 Back to Product Menu", callback_data="admin_products")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(message, reply_markup=reply_markup)

    context.user_data.clear()


async def cancel_product_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel product creation."""
    from utils import create_admin_product_menu_keyboard

    # Handle both callback query and message
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "❌ Product creation cancelled.",
            reply_markup=create_admin_product_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Product creation cancelled.",
            reply_markup=create_admin_product_menu_keyboard()
        )

    context.user_data.clear()
    return ConversationHandler.END


# ==================== CATEGORY MANAGEMENT FLOW ====================

async def create_category_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start category creation flow."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    await query.edit_message_text("📁 Create New Category\n\nPlease enter the category name:")
    return CATEGORY_NAME


async def category_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category name input."""
    context.user_data['category_name'] = update.message.text
    await update.message.reply_text("📝 Please enter the category description (or type 'skip'):")
    return CATEGORY_DESC


async def category_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category description input."""
    desc = update.message.text if update.message.text.lower() != 'skip' else ""
    context.user_data['category_desc'] = desc

    # Create category
    with get_db_session() as session:
        category = Category(
            name=context.user_data['category_name'],
            description=context.user_data['category_desc']
        )
        session.add(category)
        session.commit()

        keyboard = [
            [InlineKeyboardButton("➕ Create Another Category", callback_data="admin_create_category")],
            [InlineKeyboardButton("🔙 Back to Category Menu", callback_data="admin_manage_categories")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"✅ Category '{category.name}' created successfully!\nCategory ID: #{category.id}",
            reply_markup=reply_markup
        )

    context.user_data.clear()
    return ConversationHandler.END


# ==================== SUBCATEGORY MANAGEMENT FLOW ====================

async def create_subcategory_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start subcategory creation flow."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    # Show categories
    with get_db_session() as session:
        categories = session.query(Category).all()

        if not categories:
            await query.edit_message_text("❌ No categories available. Please create a category first.")
            return ConversationHandler.END

        keyboard = []
        for cat in categories:
            keyboard.append([InlineKeyboardButton(cat.name, callback_data=f"subcat_cat_{cat.id}")])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_subcat")])

        await query.edit_message_text(
            "📂 Create New Subcategory\n\nSelect parent category:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return SUBCATEGORY_CATEGORY


async def subcategory_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection for subcategory."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_subcat":
        from utils import create_admin_category_menu_keyboard
        await query.edit_message_text(
            "❌ Subcategory creation cancelled.",
            reply_markup=create_admin_category_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END

    category_id = int(query.data.split("_")[-1])
    context.user_data['subcategory_category'] = category_id

    await query.edit_message_text("📝 Please enter the subcategory name:")
    return SUBCATEGORY_NAME


async def subcategory_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subcategory name input."""
    # Create subcategory
    with get_db_session() as session:
        subcategory = Subcategory(
            name=update.message.text,
            category_id=context.user_data['subcategory_category']
        )
        session.add(subcategory)
        session.commit()

        category = session.query(Category).filter_by(id=subcategory.category_id).first()

        keyboard = [
            [InlineKeyboardButton("➕ Create Another Subcategory", callback_data="admin_create_subcategory")],
            [InlineKeyboardButton("🔙 Back to Category Menu", callback_data="admin_manage_categories")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"✅ Subcategory '{subcategory.name}' created under '{category.name}'!\n"
            f"Subcategory ID: #{subcategory.id}",
            reply_markup=reply_markup
        )

    context.user_data.clear()
    return ConversationHandler.END


# ==================== CATEGORY EDIT FLOW ====================

async def edit_category_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start category edit flow - show paginated category list."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    # Get page number from callback data (default to 0)
    page = 0
    if "_page_" in query.data:
        page = int(query.data.split("_page_")[1])

    with get_db_session() as session:
        # Get all categories
        all_categories = session.query(Category).order_by(Category.id).all()

        if not all_categories:
            await query.edit_message_text(
                "❌ No categories found. Please create a category first.",
                reply_markup=create_admin_category_menu_keyboard()
            )
            return ConversationHandler.END

        # Pagination settings
        items_per_page = 5
        total_pages = (len(all_categories) + items_per_page - 1) // items_per_page
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        categories = all_categories[start_idx:end_idx]

        # Build category selection keyboard
        keyboard = []
        for category in categories:
            keyboard.append([
                InlineKeyboardButton(
                    f"📁 {category.name}",
                    callback_data=f"edit_cat_{category.id}"
                )
            ])

        # Add pagination buttons if needed
        if total_pages > 1:
            pagination_row = []
            if page > 0:
                pagination_row.append(InlineKeyboardButton("◀️ Previous", callback_data=f"admin_edit_category_page_{page-1}"))
            pagination_row.append(InlineKeyboardButton(f"Page {page+1}/{total_pages}", callback_data="noop"))
            if page < total_pages - 1:
                pagination_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"admin_edit_category_page_{page+1}"))
            keyboard.append(pagination_row)

        # Add back button
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_manage_categories")])

        await query.edit_message_text(
            "✏️ Edit Category\n\nSelect a category to edit:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EDIT_CATEGORY_SELECT


async def edit_category_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection from the list."""
    query = update.callback_query
    await query.answer()

    # Handle back button
    if query.data == "admin_manage_categories":
        from utils import create_admin_category_menu_keyboard
        await query.edit_message_text(
            "📁 Category Management",
            reply_markup=create_admin_category_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END

    # Handle pagination - stay in EDIT_CATEGORY_SELECT state
    if "admin_edit_category_page_" in query.data:
        return await edit_category_start(update, context)

    # Extract category ID from callback data
    category_id = int(query.data.split("_")[2])

    with get_db_session() as session:
        category = session.query(Category).filter_by(id=category_id).first()

        if not category:
            await query.edit_message_text(
                "❌ Category not found.",
                reply_markup=create_admin_category_menu_keyboard()
            )
            return ConversationHandler.END

        context.user_data['edit_category_id'] = category_id

        # Show fields to edit
        keyboard = [
            [InlineKeyboardButton("📦 Name", callback_data="editcat_name")],
            [InlineKeyboardButton("📝 Description", callback_data="editcat_desc")],
            [InlineKeyboardButton("🗑 Delete Category", callback_data="editcat_delete")],
            [InlineKeyboardButton("🔙 Cancel", callback_data="cancel_edit_cat")]
        ]

        await query.edit_message_text(
            f"Editing Category: {category.name}\n"
            f"Description: {category.description or 'No description'}\n\n"
            f"What would you like to do?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EDIT_CATEGORY_FIELD


async def edit_category_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle field selection for category editing."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_edit_cat":
        from utils import create_admin_category_menu_keyboard
        await query.edit_message_text(
            "❌ Category edit cancelled.",
            reply_markup=create_admin_category_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "editcat_delete":
        # Delete category only - products and subcategories remain (can be reassigned)
        with get_db_session() as session:
            from database import Cart
            category = session.query(Category).filter_by(id=context.user_data['edit_category_id']).first()
            category_name = category.name

            # Count affected items
            products_count = session.query(Product).filter_by(category_id=category.id).count()
            subcats_count = session.query(Subcategory).filter_by(category_id=category.id).count()

            # Delete cart items and unlink products from category
            products = session.query(Product).filter_by(category_id=category.id).all()
            for product in products:
                session.query(Cart).filter_by(product_id=product.id).delete()
                product.category_id = None

            # Unlink subcategories from category
            subcategories = session.query(Subcategory).filter_by(category_id=category.id).all()
            for subcat in subcategories:
                subcat.category_id = None

            # Delete the category
            session.delete(category)
            session.commit()
            from utils import create_admin_category_menu_keyboard
            await query.edit_message_text(
                f"✅ Category '{category_name}' deleted successfully!\n\n"
                f"Note: {products_count} product(s) and {subcats_count} subcategory(ies) "
                f"remain and can be reassigned to another category.",
                reply_markup=create_admin_category_menu_keyboard()
            )

        context.user_data.clear()
        return ConversationHandler.END

    context.user_data['edit_category_field'] = query.data.split("_")[1]
    field = context.user_data['edit_category_field']

    # Get current category data to show old value
    with get_db_session() as session:
        category = session.query(Category).filter_by(id=context.user_data['edit_category_id']).first()

        if field == 'name':
            prompt = f"📦 Current name: {category.name}\n\nEnter new category name:"
        elif field == 'desc':
            prompt = f"📝 Current description:\n{category.description or 'No description'}\n\nEnter new category description (or type 'skip' to remove):"

    cancel_keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit_cat")]]
    await query.edit_message_text(
        prompt,
        reply_markup=InlineKeyboardMarkup(cancel_keyboard)
    )
    return EDIT_CATEGORY_VALUE


async def edit_category_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new value input for edited category field."""
    field = context.user_data['edit_category_field']
    new_value = update.message.text

    with get_db_session() as session:
        category = session.query(Category).filter_by(id=context.user_data['edit_category_id']).first()

        if field == 'name':
            category.name = new_value
        elif field == 'desc':
            category.description = "" if new_value.lower() == 'skip' else new_value

        session.commit()

        from utils import create_admin_category_menu_keyboard
        keyboard = [
            [InlineKeyboardButton("✏️ Edit Another Category", callback_data="admin_edit_category")],
            [InlineKeyboardButton("🔙 Back to Category Menu", callback_data="admin_manage_categories")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"✅ Category {field} updated successfully!",
            reply_markup=reply_markup
        )

    context.user_data.clear()
    return ConversationHandler.END


# ==================== SUBCATEGORY EDIT FLOW ====================

async def edit_subcategory_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start subcategory edit flow - show paginated subcategory list."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    # Get page number from callback data (default to 0)
    page = 0
    if "_page_" in query.data:
        page = int(query.data.split("_page_")[1])

    with get_db_session() as session:
        # Get all subcategories with their parent categories
        all_subcategories = session.query(Subcategory).order_by(Subcategory.id).all()

        if not all_subcategories:
            from utils import create_admin_category_menu_keyboard
            await query.edit_message_text(
                "❌ No subcategories found. Please create a subcategory first.",
                reply_markup=create_admin_category_menu_keyboard()
            )
            return ConversationHandler.END

        # Pagination settings
        items_per_page = 5
        total_pages = (len(all_subcategories) + items_per_page - 1) // items_per_page
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        subcategories = all_subcategories[start_idx:end_idx]

        # Build subcategory selection keyboard
        keyboard = []
        for subcategory in subcategories:
            category = session.query(Category).filter_by(id=subcategory.category_id).first() if subcategory.category_id else None
            category_label = category.name if category else "No Category"
            keyboard.append([
                InlineKeyboardButton(
                    f"📂 {subcategory.name} (in {category_label})",
                    callback_data=f"edit_subcat_{subcategory.id}"
                )
            ])

        # Add pagination buttons if needed
        if total_pages > 1:
            pagination_row = []
            if page > 0:
                pagination_row.append(InlineKeyboardButton("◀️ Previous", callback_data=f"admin_edit_subcategory_page_{page-1}"))
            pagination_row.append(InlineKeyboardButton(f"Page {page+1}/{total_pages}", callback_data="noop"))
            if page < total_pages - 1:
                pagination_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"admin_edit_subcategory_page_{page+1}"))
            keyboard.append(pagination_row)

        # Add back button
        from utils import create_admin_category_menu_keyboard
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_manage_categories")])

        await query.edit_message_text(
            "✏️ Edit Subcategory\n\nSelect a subcategory to edit:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EDIT_SUBCATEGORY_SELECT


async def edit_subcategory_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subcategory selection from the list."""
    query = update.callback_query
    await query.answer()

    # Handle back button
    if query.data == "admin_manage_categories":
        from utils import create_admin_category_menu_keyboard
        await query.edit_message_text(
            "📁 Category Management",
            reply_markup=create_admin_category_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END

    # Handle pagination - stay in EDIT_SUBCATEGORY_SELECT state
    if "admin_edit_subcategory_page_" in query.data:
        return await edit_subcategory_start(update, context)

    # Extract subcategory ID from callback data
    subcategory_id = int(query.data.split("_")[2])

    with get_db_session() as session:
        subcategory = session.query(Subcategory).filter_by(id=subcategory_id).first()

        if not subcategory:
            from utils import create_admin_category_menu_keyboard
            await query.edit_message_text(
                "❌ Subcategory not found.",
                reply_markup=create_admin_category_menu_keyboard()
            )
            return ConversationHandler.END

        category = session.query(Category).filter_by(id=subcategory.category_id).first() if subcategory.category_id else None
        category_name = category.name if category else "No Category"
        context.user_data['edit_subcategory_id'] = subcategory_id

        # Show fields to edit
        keyboard = [
            [InlineKeyboardButton("📦 Name", callback_data="editsubcat_name")],
            [InlineKeyboardButton("📁 Change Parent Category", callback_data="editsubcat_category")],
            [InlineKeyboardButton("🗑 Delete Subcategory", callback_data="editsubcat_delete")],
            [InlineKeyboardButton("🔙 Cancel", callback_data="cancel_edit_subcat")]
        ]

        await query.edit_message_text(
            f"Editing Subcategory: {subcategory.name}\n"
            f"Parent Category: {category_name}\n\n"
            f"What would you like to do?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EDIT_SUBCATEGORY_FIELD


async def edit_subcategory_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle field selection for subcategory editing."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_edit_subcat":
        from utils import create_admin_category_menu_keyboard
        await query.edit_message_text(
            "❌ Subcategory edit cancelled.",
            reply_markup=create_admin_category_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "editsubcat_delete":
        # Delete subcategory only - products remain (can be reassigned)
        with get_db_session() as session:
            from database import Cart
            subcategory = session.query(Subcategory).filter_by(id=context.user_data['edit_subcategory_id']).first()
            subcategory_name = subcategory.name

            # Get products in this subcategory
            products = session.query(Product).filter_by(subcategory_id=subcategory.id).all()
            products_count = len(products)

            # Delete cart items and unlink products from subcategory
            for product in products:
                session.query(Cart).filter_by(product_id=product.id).delete()
                product.subcategory_id = None

            session.delete(subcategory)
            session.commit()
            from utils import create_admin_category_menu_keyboard
            await query.edit_message_text(
                f"✅ Subcategory '{subcategory_name}' deleted successfully!\n\n"
                f"Note: {products_count} product(s) remain and can be reassigned to another subcategory.",
                reply_markup=create_admin_category_menu_keyboard()
            )

        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "editsubcat_category":
        # Show category selection
        with get_db_session() as session:
            categories = session.query(Category).all()

            if not categories:
                from utils import create_admin_category_menu_keyboard
                await query.edit_message_text(
                    "❌ No categories available.",
                    reply_markup=create_admin_category_menu_keyboard()
                )
                context.user_data.clear()
                return ConversationHandler.END

            keyboard = []
            for cat in categories:
                keyboard.append([InlineKeyboardButton(cat.name, callback_data=f"newcat_{cat.id}")])
            keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit_subcat")])

            context.user_data['edit_subcategory_field'] = 'category'

            await query.edit_message_text(
                "📁 Select new parent category:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return EDIT_SUBCATEGORY_VALUE

    context.user_data['edit_subcategory_field'] = query.data.split("_")[1]
    field = context.user_data['edit_subcategory_field']

    # Get current subcategory data to show old value
    with get_db_session() as session:
        subcategory = session.query(Subcategory).filter_by(id=context.user_data['edit_subcategory_id']).first()

        if field == 'name':
            prompt = f"📦 Current name: {subcategory.name}\n\nEnter new subcategory name:"

    cancel_keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit_subcat")]]
    await query.edit_message_text(
        prompt,
        reply_markup=InlineKeyboardMarkup(cancel_keyboard)
    )
    return EDIT_SUBCATEGORY_VALUE


async def edit_subcategory_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new value input for edited subcategory field."""
    field = context.user_data['edit_subcategory_field']

    with get_db_session() as session:
        subcategory = session.query(Subcategory).filter_by(id=context.user_data['edit_subcategory_id']).first()

        if field == 'name':
            new_value = update.message.text
            subcategory.name = new_value
        elif field == 'category':
            # Handle category change via callback
            query = update.callback_query
            await query.answer()

            if query.data == "cancel_edit_subcat":
                from utils import create_admin_category_menu_keyboard
                await query.edit_message_text(
                    "❌ Subcategory edit cancelled.",
                    reply_markup=create_admin_category_menu_keyboard()
                )
                context.user_data.clear()
                return ConversationHandler.END

            new_category_id = int(query.data.split("_")[1])
            subcategory.category_id = new_category_id

        session.commit()

        from utils import create_admin_category_menu_keyboard
        keyboard = [
            [InlineKeyboardButton("✏️ Edit Another Subcategory", callback_data="admin_edit_subcategory")],
            [InlineKeyboardButton("🔙 Back to Category Menu", callback_data="admin_manage_categories")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if field == 'category':
            await query.edit_message_text(
                f"✅ Subcategory parent category updated successfully!",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                f"✅ Subcategory {field} updated successfully!",
                reply_markup=reply_markup
            )

    context.user_data.clear()
    return ConversationHandler.END


# ==================== PRODUCT EDIT FLOW ====================

async def edit_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start product edit flow - show paginated product list."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    # Get page number from callback data (default to 0)
    page = 0
    if "_page_" in query.data:
        page = int(query.data.split("_page_")[1])

    with get_db_session() as session:
        # Get all products
        all_products = session.query(Product).order_by(Product.id).all()

        if not all_products:
            await query.edit_message_text(
                "❌ No products found. Please create a product first.",
                reply_markup=create_admin_product_menu_keyboard()
            )
            return ConversationHandler.END

        # Pagination settings
        items_per_page = 5
        total_pages = (len(all_products) + items_per_page - 1) // items_per_page
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        products = all_products[start_idx:end_idx]

        # Build product selection keyboard
        keyboard = []
        for product in products:
            status_icon = "✅" if product.is_active else "❌"
            keyboard.append([
                InlineKeyboardButton(
                    f"{status_icon} {product.name} (${product.price})",
                    callback_data=f"edit_prod_{product.id}"
                )
            ])

        # Add pagination buttons if needed
        if total_pages > 1:
            pagination_row = []
            if page > 0:
                pagination_row.append(InlineKeyboardButton("◀️ Previous", callback_data=f"admin_edit_product_page_{page-1}"))
            pagination_row.append(InlineKeyboardButton(f"Page {page+1}/{total_pages}", callback_data="noop"))
            if page < total_pages - 1:
                pagination_row.append(InlineKeyboardButton("Next ▶️", callback_data=f"admin_edit_product_page_{page+1}"))
            keyboard.append(pagination_row)

        # Add cancel button
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="admin_products")])

        await query.edit_message_text(
            "✏️ Edit Product\n\nSelect a product to edit:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EDIT_SELECT_PRODUCT


async def edit_select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product selection from the list."""
    query = update.callback_query
    await query.answer()

    # Handle pagination - stay in EDIT_SELECT_PRODUCT state
    if "admin_edit_product_page_" in query.data:
        return await edit_product_start(update, context)

    # Extract product ID from callback data
    product_id = int(query.data.split("_")[2])

    with get_db_session() as session:
        product = session.query(Product).filter_by(id=product_id).first()

        if not product:
            await query.edit_message_text(
                "❌ Product not found.",
                reply_markup=create_admin_product_menu_keyboard()
            )
            return ConversationHandler.END

        context.user_data['edit_product_id'] = product_id

        # Get current category and subcategory names
        category_name = "None"
        subcategory_name = "None"
        if product.category_id:
            category = session.query(Category).filter_by(id=product.category_id).first()
            category_name = category.name if category else "None"
        if product.subcategory_id:
            subcategory = session.query(Subcategory).filter_by(id=product.subcategory_id).first()
            subcategory_name = subcategory.name if subcategory else "None"

        # Get available keys count
        from database import ProductKey
        available_keys = session.query(ProductKey).filter_by(product_id=product.id, is_sold=False).count()

        # Show fields to edit
        keyboard = [
            [InlineKeyboardButton("📦 Name", callback_data="edit_name")],
            [InlineKeyboardButton("📝 Description", callback_data="edit_desc")],
            [InlineKeyboardButton("💰 Price", callback_data="edit_price")],
            [InlineKeyboardButton("🖼 Image", callback_data="edit_image")],
            [InlineKeyboardButton("📁 Category", callback_data="edit_category")],
            [InlineKeyboardButton("📂 Subcategory", callback_data="edit_subcategory")],
            [InlineKeyboardButton("✅ Activate", callback_data="edit_activate")],
            [InlineKeyboardButton("❌ Deactivate", callback_data="edit_deactivate")],
            [InlineKeyboardButton(f"🗑 Clear Keys ({available_keys})", callback_data="edit_clear_keys")],
            [InlineKeyboardButton("🗑 Delete Product", callback_data="edit_delete")],
            [InlineKeyboardButton("🔙 Cancel", callback_data="cancel_edit")]
        ]

        current_status = "Active" if product.is_active else "Inactive"

        await query.edit_message_text(
            f"Editing Product: {product.name}\n"
            f"Current Price: {format_price(product.price)}\n"
            f"Category: {category_name}\n"
            f"Subcategory: {subcategory_name}\n"
            f"Status: {current_status}\n"
            f"Available Keys: {available_keys}\n\n"
            f"What would you like to edit?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EDIT_SELECT_FIELD


async def edit_select_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle field selection for editing."""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_edit":
        await query.edit_message_text(
            "❌ Product edit cancelled.",
            reply_markup=create_admin_product_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "edit_activate":
        # Activate product
        with get_db_session() as session:
            product = session.query(Product).filter_by(id=context.user_data['edit_product_id']).first()
            product.is_active = True
            session.commit()
            await query.edit_message_text(
                f"✅ Product '{product.name}' activated!",
                reply_markup=create_admin_product_menu_keyboard()
            )
        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "edit_deactivate":
        # Deactivate product
        with get_db_session() as session:
            product = session.query(Product).filter_by(id=context.user_data['edit_product_id']).first()
            product.is_active = False
            session.commit()
            await query.edit_message_text(
                f"❌ Product '{product.name}' deactivated!",
                reply_markup=create_admin_product_menu_keyboard()
            )
        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "edit_clear_keys":
        # Clear all unsold keys for the product
        with get_db_session() as session:
            from database import ProductKey
            product = session.query(Product).filter_by(id=context.user_data['edit_product_id']).first()
            product_name = product.name

            # Count and delete only unsold keys
            unsold_keys_count = session.query(ProductKey).filter_by(
                product_id=product.id, is_sold=False
            ).count()

            if unsold_keys_count == 0:
                await query.edit_message_text(
                    f"ℹ️ Product '{product_name}' has no unsold keys to clear.",
                    reply_markup=create_admin_product_menu_keyboard()
                )
            else:
                session.query(ProductKey).filter_by(
                    product_id=product.id, is_sold=False
                ).delete()
                # Update stock count
                product.stock_count = 0
                session.commit()
                await query.edit_message_text(
                    f"✅ Cleared {unsold_keys_count} unsold key(s) from '{product_name}'!\n\n"
                    f"You can now add new keys using the Restock option.",
                    reply_markup=create_admin_product_menu_keyboard()
                )
        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "edit_delete":
        # Delete product only - order items remain (preserve order history)
        with get_db_session() as session:
            from database import Cart, ProductKey
            product = session.query(Product).filter_by(id=context.user_data['edit_product_id']).first()
            product_name = product.name

            # Delete associated cart items
            session.query(Cart).filter_by(product_id=product.id).delete()
            # Delete only unsold product keys (sold keys remain for order history)
            session.query(ProductKey).filter_by(product_id=product.id, is_sold=False).delete()
            # Delete the product (order items remain with orphaned product_id)
            session.delete(product)
            session.commit()
            await query.edit_message_text(
                f"✅ Product '{product_name}' deleted successfully!\n\n"
                f"Note: Order history is preserved.",
                reply_markup=create_admin_product_menu_keyboard()
            )

        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "edit_image":
        # Prompt for new image
        with get_db_session() as session:
            product = session.query(Product).filter_by(id=context.user_data['edit_product_id']).first()

            current_image_status = "Has image" if (product.image_path and os.path.exists(product.image_path)) else "No image"

            keyboard = [
                [InlineKeyboardButton("🗑 Remove Image", callback_data="remove_product_image")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")]
            ]

            await query.edit_message_text(
                f"🖼 Product: {product.name}\n"
                f"Current: {current_image_status}\n\n"
                f"Send a new product image or use the buttons below:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return EDIT_IMAGE_VALUE

    if query.data == "edit_category":
        # Show category selection
        with get_db_session() as session:
            categories = session.query(Category).all()

            if not categories:
                await query.edit_message_text(
                    "❌ No categories available. Please create a category first.",
                    reply_markup=create_admin_product_menu_keyboard()
                )
                context.user_data.clear()
                return ConversationHandler.END

            keyboard = []
            for cat in categories:
                keyboard.append([InlineKeyboardButton(cat.name, callback_data=f"newprodcat_{cat.id}")])
            keyboard.append([InlineKeyboardButton("🗑 Remove Category", callback_data="newprodcat_none")])
            keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")])

            context.user_data['edit_field'] = 'category'

            await query.edit_message_text(
                "📁 Select new category for this product:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return EDIT_NEW_VALUE

    if query.data == "edit_subcategory":
        # Show subcategory selection
        with get_db_session() as session:
            # Get product to know current category
            product = session.query(Product).filter_by(id=context.user_data['edit_product_id']).first()

            # Get subcategories (optionally filter by product's category)
            if product.category_id:
                subcategories = session.query(Subcategory).filter_by(category_id=product.category_id).all()
            else:
                subcategories = session.query(Subcategory).all()

            keyboard = []
            if subcategories:
                for subcat in subcategories:
                    keyboard.append([InlineKeyboardButton(subcat.name, callback_data=f"newprodsubcat_{subcat.id}")])
            keyboard.append([InlineKeyboardButton("🗑 Remove Subcategory", callback_data="newprodsubcat_none")])
            keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")])

            context.user_data['edit_field'] = 'subcategory'

            await query.edit_message_text(
                "📂 Select new subcategory for this product:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return EDIT_NEW_VALUE

    context.user_data['edit_field'] = query.data.split("_")[1]
    field = context.user_data['edit_field']

    # Get current product data to show old value
    with get_db_session() as session:
        product = session.query(Product).filter_by(id=context.user_data['edit_product_id']).first()

        if field == 'name':
            prompt = f"📦 Current name: {product.name}\n\nEnter new product name:"
        elif field == 'desc':
            prompt = f"📝 Current description:\n{product.description}\n\nEnter new product description:"
        elif field == 'price':
            prompt = f"💰 Current price: {format_price(product.price)}\n\nEnter new product price (USD):"

    cancel_keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")]]
    await query.edit_message_text(
        prompt,
        reply_markup=InlineKeyboardMarkup(cancel_keyboard)
    )
    return EDIT_NEW_VALUE


async def edit_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new value input for edited field."""
    field = context.user_data['edit_field']

    # Handle category and subcategory changes (callback queries)
    if field in ['category', 'subcategory']:
        query = update.callback_query
        await query.answer()

        if query.data == "cancel_edit":
            await query.edit_message_text(
                "❌ Product edit cancelled.",
                reply_markup=create_admin_product_menu_keyboard()
            )
            context.user_data.clear()
            return ConversationHandler.END

        with get_db_session() as session:
            product = session.query(Product).filter_by(id=context.user_data['edit_product_id']).first()

            if field == 'category':
                if query.data == "newprodcat_none":
                    product.category_id = None
                    product.subcategory_id = None  # Clear subcategory when removing category
                else:
                    new_category_id = int(query.data.split("_")[1])
                    product.category_id = new_category_id
                    # Clear subcategory if it doesn't belong to new category
                    if product.subcategory_id:
                        subcat = session.query(Subcategory).filter_by(id=product.subcategory_id).first()
                        if subcat and subcat.category_id != new_category_id:
                            product.subcategory_id = None

            elif field == 'subcategory':
                if query.data == "newprodsubcat_none":
                    product.subcategory_id = None
                else:
                    new_subcategory_id = int(query.data.split("_")[1])
                    product.subcategory_id = new_subcategory_id
                    # Update category to match subcategory's parent
                    subcat = session.query(Subcategory).filter_by(id=new_subcategory_id).first()
                    if subcat:
                        product.category_id = subcat.category_id

            session.commit()

            keyboard = [
                [InlineKeyboardButton("✏️ Edit Another Product", callback_data="admin_edit_product")],
                [InlineKeyboardButton("🔙 Back to Product Menu", callback_data="admin_products")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"✅ Product {field} updated successfully!",
                reply_markup=reply_markup
            )

        context.user_data.clear()
        return ConversationHandler.END

    # Handle text input (name, desc, price)
    new_value = update.message.text

    with get_db_session() as session:
        product = session.query(Product).filter_by(id=context.user_data['edit_product_id']).first()

        if field == 'name':
            product.name = new_value
        elif field == 'desc':
            product.description = new_value
        elif field == 'price':
            try:
                product.price = float(new_value)
            except ValueError:
                cancel_keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_edit")]]
                await update.message.reply_text(
                    "❌ Invalid price. Please enter a valid number:",
                    reply_markup=InlineKeyboardMarkup(cancel_keyboard)
                )
                return EDIT_NEW_VALUE

        session.commit()

        keyboard = [
            [InlineKeyboardButton("✏️ Edit Another Product", callback_data="admin_edit_product")],
            [InlineKeyboardButton("🔙 Back to Product Menu", callback_data="admin_products")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"✅ Product {field} updated successfully!",
            reply_markup=reply_markup
        )

    context.user_data.clear()
    return ConversationHandler.END


async def edit_image_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product image edit - receives new image or remove command."""
    # Handle callback queries (remove image or cancel)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == "cancel_edit":
            await query.edit_message_text(
                "❌ Product edit cancelled.",
                reply_markup=create_admin_product_menu_keyboard()
            )
            context.user_data.clear()
            return ConversationHandler.END

        if query.data == "remove_product_image":
            # Remove product image
            with get_db_session() as session:
                product = session.query(Product).filter_by(id=context.user_data['edit_product_id']).first()

                # Delete old image file if exists
                if product.image_path and os.path.exists(product.image_path):
                    try:
                        os.remove(product.image_path)
                    except Exception as e:
                        print(f"Error deleting old image: {e}")

                product.image_path = None
                session.commit()

                keyboard = [
                    [InlineKeyboardButton("✏️ Edit Another Product", callback_data="admin_edit_product")],
                    [InlineKeyboardButton("🔙 Back to Product Menu", callback_data="admin_products")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    f"✅ Product image removed successfully!",
                    reply_markup=reply_markup
                )

            context.user_data.clear()
            return ConversationHandler.END

    # Handle photo upload
    if update.message and update.message.photo:
        photo = update.message.photo[-1]  # Get highest resolution
        file = await context.bot.get_file(photo.file_id)

        # Create products directory if not exists
        products_dir = app_settings.PRODUCTS_DIR
        os.makedirs(products_dir, exist_ok=True)

        # Save with unique filename
        image_path = os.path.join(products_dir, f"product_{context.user_data['edit_product_id']}_{photo.file_id}.jpg")
        await file.download_to_drive(image_path)

        # Update product with new image
        with get_db_session() as session:
            product = session.query(Product).filter_by(id=context.user_data['edit_product_id']).first()

            # Delete old image file if exists
            if product.image_path and os.path.exists(product.image_path):
                try:
                    os.remove(product.image_path)
                except Exception as e:
                    print(f"Error deleting old image: {e}")

            product.image_path = image_path
            session.commit()

            keyboard = [
                [InlineKeyboardButton("✏️ Edit Another Product", callback_data="admin_edit_product")],
                [InlineKeyboardButton("🔙 Back to Product Menu", callback_data="admin_products")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"✅ Product image updated successfully!",
                reply_markup=reply_markup
            )

        context.user_data.clear()
        return ConversationHandler.END

    # Invalid input
    await update.message.reply_text(
        "❌ Please send an image or use the buttons provided."
    )
    return EDIT_IMAGE_VALUE


# ==================== SETTINGS CONFIGURATION ====================

async def config_support_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start support username configuration."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    context.user_data['setting_type'] = 'support_username'

    # Get current support username
    with get_db_session() as session:
        settings = session.query(Settings).first()
        current_value = settings.support_username if settings and settings.support_username else "Not set"

    await query.edit_message_text(
        f"📞 Current support username: @{current_value}\n\nEnter the new support Telegram username (without @):"
    )
    return SETTING_VALUE


async def config_channel_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start channel username configuration."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    context.user_data['setting_type'] = 'channel_username'

    # Get current channel username
    with get_db_session() as session:
        settings = session.query(Settings).first()
        current_value = settings.channel_username if settings and settings.channel_username else "Not set"

    await query.edit_message_text(
        f"📢 Current channel username: @{current_value}\n\nEnter the new channel/group Telegram username (without @):"
    )
    return SETTING_VALUE


async def setting_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle setting value input."""
    setting_type = context.user_data['setting_type']
    value = update.message.text.strip().replace('@', '')

    with get_db_session() as session:
        settings = session.query(Settings).first()

        if not settings:
            settings = Settings()
            session.add(settings)

        if setting_type == 'support_username':
            settings.support_username = value
            await update.message.reply_text(f"✅ Support username set to: @{value}")
        elif setting_type == 'channel_username':
            settings.channel_username = value
            await update.message.reply_text(f"✅ Channel username set to: @{value}")

        settings.updated_at = datetime.utcnow()
        session.commit()

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generic cancel handler for conversations."""
    from utils import create_admin_category_menu_keyboard

    # Handle both callback queries and messages
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "❌ Operation cancelled.",
            reply_markup=create_admin_category_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Operation cancelled.",
            reply_markup=create_admin_category_menu_keyboard()
        )

    context.user_data.clear()
    return ConversationHandler.END


# ==================== BROADCAST FLOW ====================

async def broadcast_text_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start text-only broadcast flow."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    from utils import create_cancel_keyboard
    await query.edit_message_text(
        "💬 Text Only Broadcast\n\n"
        "Please send the message you want to broadcast to all users:",
        reply_markup=create_cancel_keyboard()
    )
    return BROADCAST_TEXT


async def broadcast_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast text message and send to all users."""
    from database import get_db_session, User
    from utils import create_admin_broadcast_menu_keyboard

    message_text = update.message.text

    # Get all users
    with get_db_session() as session:
        users = session.query(User).all()

        if not users:
            await update.message.reply_text(
                "❌ No users found in the database.",
                reply_markup=create_admin_broadcast_menu_keyboard()
            )
            context.user_data.clear()
            return ConversationHandler.END

        # Send broadcast to all users with rate limiting
        success_count = 0
        fail_count = 0

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=message_text
                )
                success_count += 1
                # Rate limiting: 50ms delay = ~20 messages/second (well under Telegram's 30/sec limit)
                import asyncio
                await asyncio.sleep(0.05)
            except Exception:
                fail_count += 1

        # Show results
        result_msg = f"✅ Broadcast Complete!\n\n"
        result_msg += f"📊 Results:\n"
        result_msg += f"✅ Sent successfully: {success_count}\n"
        result_msg += f"❌ Failed: {fail_count}\n"
        result_msg += f"👥 Total users: {len(users)}"

        await update.message.reply_text(
            result_msg,
            reply_markup=create_admin_broadcast_menu_keyboard()
        )

    context.user_data.clear()
    return ConversationHandler.END


async def broadcast_image_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start image+text broadcast flow."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    from utils import create_cancel_keyboard
    await query.edit_message_text(
        "🖼 Image + Text Broadcast\n\n"
        "Step 1/2: Please send the image you want to broadcast:",
        reply_markup=create_cancel_keyboard()
    )
    return BROADCAST_IMAGE


async def broadcast_image_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast image and ask for caption text."""
    from utils import create_cancel_keyboard

    # Store the photo file_id
    context.user_data['broadcast_image_file_id'] = update.message.photo[-1].file_id

    await update.message.reply_text(
        "✅ Image received!\n\n"
        "Step 2/2: Please send the text/caption for this broadcast:",
        reply_markup=create_cancel_keyboard()
    )
    return BROADCAST_TEXT


async def broadcast_image_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast caption text and send image+text to all users."""
    from database import get_db_session, User
    from utils import create_admin_broadcast_menu_keyboard

    caption_text = update.message.text
    image_file_id = context.user_data.get('broadcast_image_file_id')

    if not image_file_id:
        await update.message.reply_text(
            "❌ Error: Image not found. Please try again.",
            reply_markup=create_admin_broadcast_menu_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END

    # Get all users
    with get_db_session() as session:
        users = session.query(User).all()

        if not users:
            await update.message.reply_text(
                "❌ No users found in the database.",
                reply_markup=create_admin_broadcast_menu_keyboard()
            )
            context.user_data.clear()
            return ConversationHandler.END

        # Send broadcast to all users with rate limiting
        success_count = 0
        fail_count = 0

        for user in users:
            try:
                # Send image first
                await context.bot.send_photo(
                    chat_id=user.telegram_id,
                    photo=image_file_id
                )
                # Small delay between image and text
                import asyncio
                await asyncio.sleep(0.03)

                # Then send text as separate message
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=caption_text
                )
                success_count += 1

                # Rate limiting: 50ms delay = ~20 messages/second (well under Telegram's 30/sec limit)
                await asyncio.sleep(0.05)
            except Exception:
                fail_count += 1

        # Show results
        result_msg = f"✅ Broadcast Complete!\n\n"
        result_msg += f"📊 Results:\n"
        result_msg += f"✅ Sent successfully: {success_count}\n"
        result_msg += f"❌ Failed: {fail_count}\n"
        result_msg += f"👥 Total users: {len(users)}"

        await update.message.reply_text(
            result_msg,
            reply_markup=create_admin_broadcast_menu_keyboard()
        )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel broadcast flow."""
    from utils import create_admin_broadcast_menu_keyboard

    # Handle both callback query and message
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "❌ Broadcast cancelled.",
            reply_markup=create_admin_broadcast_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Broadcast cancelled.",
            reply_markup=create_admin_broadcast_menu_keyboard()
        )

    context.user_data.clear()
    return ConversationHandler.END


# ==================== WELCOME MESSAGE FLOW ====================

async def config_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start welcome message configuration flow."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    # Get current welcome message
    with get_db_session() as session:
        settings = session.query(Settings).first()
        current_msg = settings.welcome_message if settings else "Welcome to our Digital Products Store!"

    from utils import create_cancel_keyboard
    await query.edit_message_text(
        f"💬 Welcome Message Configuration\n\n"
        f"Current message:\n{current_msg}\n\n"
        f"Please send the new welcome message:",
        reply_markup=create_cancel_keyboard()
    )
    context.user_data['setting_type'] = 'welcome_message'
    return WELCOME_MESSAGE


async def welcome_message_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new welcome message value."""
    from utils import create_admin_settings_menu_keyboard

    new_message = update.message.text

    # Update welcome message in database
    with get_db_session() as session:
        settings = session.query(Settings).first()
        if not settings:
            settings = Settings()
            session.add(settings)
        
        settings.welcome_message = new_message
        session.commit()

        await update.message.reply_text(
            f"✅ Welcome message updated successfully!\n\n"
            f"New message:\n{new_message}",
            reply_markup=create_admin_settings_menu_keyboard()
        )

    context.user_data.clear()
    return ConversationHandler.END


# ==================== STORE LOGO FLOW ====================

async def config_store_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start store logo configuration flow."""
    query = update.callback_query
    await query.answer()

    if not is_admin(update.effective_user.id):
        await query.answer("⛔ Access denied.", show_alert=True)
        return ConversationHandler.END

    # Get current logo status
    with get_db_session() as session:
        settings = session.query(Settings).first()
        has_logo = settings and settings.store_logo_path and os.path.exists(settings.store_logo_path)

    from utils import create_cancel_keyboard
    status_text = "✅ Logo is set" if has_logo else "❌ No logo set"
    
    await query.edit_message_text(
        f"🖼 Store Logo Configuration\n\n"
        f"Current status: {status_text}\n\n"
        f"Please send a new image for the store logo:",
        reply_markup=create_cancel_keyboard()
    )
    context.user_data['setting_type'] = 'store_logo'
    return STORE_LOGO


async def store_logo_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new store logo image."""
    from utils import create_admin_settings_menu_keyboard

    # Get the photo
    photo = update.message.photo[-1]  # Get highest resolution
    
    # Download the photo
    file = await context.bot.get_file(photo.file_id)
    
    # Create uploads directory if it doesn't exist
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    
    # Save the file
    file_path = os.path.join(uploads_dir, f"store_logo_{photo.file_id}.jpg")
    await file.download_to_drive(file_path)

    # Update store logo path in database
    with get_db_session() as session:
        settings = session.query(Settings).first()
        if not settings:
            settings = Settings()
            session.add(settings)
        
        # Delete old logo if exists
        if settings.store_logo_path and os.path.exists(settings.store_logo_path):
            try:
                os.remove(settings.store_logo_path)
            except:
                pass
        
        settings.store_logo_path = file_path
        session.commit()

        await update.message.reply_text(
            "✅ Store logo updated successfully!",
            reply_markup=create_admin_settings_menu_keyboard()
        )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel settings configuration flow."""
    from utils import create_admin_settings_menu_keyboard

    # Handle both callback query and message
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            "❌ Configuration cancelled.",
            reply_markup=create_admin_settings_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Configuration cancelled.",
            reply_markup=create_admin_settings_menu_keyboard()
        )

    context.user_data.clear()
    return ConversationHandler.END
