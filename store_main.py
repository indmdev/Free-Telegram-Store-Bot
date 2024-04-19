import logging
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


conn = sqlite3.connect('store_products.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS products
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, price REAL, image_url TEXT, payment_instructions TEXT)''')
conn.commit()

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to the Telegram Store Bot! Use /products command to see available products.')

def create(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Enter the details of the product (name, description, price, image URL, payment instructions):')
    context.user_data['state'] = 'create'

def list_products(update: Update, context: CallbackContext) -> None:
    c.execute("SELECT * FROM products")
    rows = c.fetchall()
    if not rows:
        update.message.reply_text('No products available.')
    else:
        for row in rows:
            update.message.reply_text(f"Product ID: {row[0]}\nName: {row[1]}\nDescription: {row[2]}\nPrice: {row[3]}\nImage: {row[4]}\nPayment Instructions: {row[5]}")

def message_handler(update: Update, context: CallbackContext) -> None:
    if 'state' in context.user_data and context.user_data['state'] == 'create':
        product_details = update.message.text.split(',')
        if len(product_details) == 5:
            c.execute("INSERT INTO products (name, description, price, image_url, payment_instructions) VALUES (?, ?, ?, ?, ?)", (product_details[0], product_details[1], float(product_details[2]), product_details[3], product_details[4]))
            conn.commit()
            update.message.reply_text('Product created successfully!')
            context.user_data.clear()
        else:
            update.message.reply_text('Please provide all details (name, description, price, image URL, payment instructions) separated by commas.')
    else:
        update.message.reply_text('Invalid command.')

def cancel(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Product creation cancelled.')
    context.user_data.clear()

def main() -> None:
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("create", create))
    dispatcher.add_handler(CommandHandler("products", list_products))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dispatcher.add_handler(CommandHandler("cancel", cancel))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
