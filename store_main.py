import flask
from datetime import datetime
import requests
import time
import logging
from flask_session import Session
import telebot
from flask import Flask, request, jsonify
from telebot import types
import random
import os
import os.path
import re
from InDMDevDB import *
from purchase import *
from InDMCategories import *
from telebot.types import LabeledPrice, PreCheckoutQuery, SuccessfulPayment, ShippingOption
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# M""M M"""""""`YM M""""""'YMM M"""""`'"""`YM M""""""'YMM MM""""""""`M M""MMMMM""M 
# M  M M  mmmm.  M M  mmmm. `M M  mm.  mm.  M M  mmmm. `M MM  mmmmmmmM M  MMMMM  M 
# M  M M  MMMMM  M M  MMMMM  M M  MMM  MMM  M M  MMMMM  M M`      MMMM M  MMMMP  M 
# M  M M  MMMMM  M M  MMMMM  M M  MMM  MMM  M M  MMMMM  M MM  MMMMMMMM M  MMMM' .M 
# M  M M  MMMMM  M M  MMMM' .M M  MMM  MMM  M M  MMMM' .M MM  MMMMMMMM M  MMP' .MM 
# M  M M  MMMMM  M M       .MM M  MMM  MMM  M M       .MM MM        .M M     .dMMM 
# MMMM MMMMMMMMMMM MMMMMMMMMMM MMMMMMMMMMMMMM MMMMMMMMMMM MMMMMMMMMMMM MMMMMMMMMMM 

# Flask connection 
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Bot connection
webhook_url = os.getenv('NGROK_HTTPS_URL')
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
store_currency = os.getenv('STORE_CURRENCY', 'USD')

if not webhook_url or not bot_token:
    logger.error("Missing required environment variables: NGROK_HTTPS_URL or TELEGRAM_BOT_TOKEN")
    exit(1)

bot = telebot.TeleBot(bot_token, threaded=False)

# Set up webhook
try:
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set successfully to {webhook_url}")
except Exception as e:
    logger.error(f"Failed to set webhook: {e}")
    exit(1)


# Process webhook calls
logger.info("Shop Started!")

@flask_app.route('/', methods=['GET', 'POST'])
def webhook():
    """Handle incoming webhook requests from Telegram"""
    try:
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        
        logger.warning("Invalid content type in webhook request")
        flask.abort(403)
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        flask.abort(500)

# Initialize payment settings
def get_payment_api_key():
    """Get payment API key from database"""
    try:
        api_key = GetDataFromDB.GetPaymentMethodTokenKeysCleintID("Bitcoin")
        return api_key
    except Exception as e:
        logger.error(f"Error getting payment API key: {e}")
        return None

NOWPAYMENTS_API_KEY = get_payment_api_key()
BASE_CURRENCY = store_currency


# Create main keyboard
def create_main_keyboard():
    """Create the main user keyboard"""
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    key1 = types.KeyboardButton(text="Shop Items 🛒")
    key2 = types.KeyboardButton(text="My Orders 🛍")
    key3 = types.KeyboardButton(text="Support 📞")
    keyboard.add(key1)
    keyboard.add(key2, key3)
    return keyboard

keyboard = create_main_keyboard()


def create_admin_keyboard():
    """Create the admin keyboard"""
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    key0 = types.KeyboardButton(text="Manage Products 💼")
    key1 = types.KeyboardButton(text="Manage Categories 💼")
    key2 = types.KeyboardButton(text="Manage Orders 🛍")
    key3 = types.KeyboardButton(text="Payment Methods 💳")
    key4 = types.KeyboardButton(text="News To Users 📣")
    key5 = types.KeyboardButton(text="Switch To User 🙍‍♂️")
    keyboardadmin.add(key0)
    keyboardadmin.add(key1, key2)
    keyboardadmin.add(key3, key4)
    keyboardadmin.add(key5)
    return keyboardadmin


def create_user_keyboard():
    """Create the user keyboard"""
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    key1 = types.KeyboardButton(text="Shop Items 🛒")
    key2 = types.KeyboardButton(text="My Orders 🛍")
    key3 = types.KeyboardButton(text="Support 📞")
    key4 = types.KeyboardButton(text="Home 🏘")
    keyboard.add(key1)
    keyboard.add(key2, key3)
    keyboard.add(key4)
    return keyboard


def is_admin(user_id, admins):
    """Check if user is an admin"""
    return f"{user_id}" in f"{admins}"


def ensure_user_exists(user_id, username):
    """Ensure user exists in database"""
    users = GetDataFromDB.GetUserIDsInDB()
    if f"{user_id}" not in f"{users}":
        CreateDatas.AddAuser(user_id, username)


##################WELCOME MESSAGE + BUTTONS START#########################
#Function to list Products and Categories
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Handle callback queries from inline keyboards"""
    try:
        if call.data.startswith("getcats_"):
            input_catees = call.data.replace('getcats_','')
            CategoriesDatas.get_category_products(call, input_catees)
            return
        
        if call.data.startswith("getproduct_"):
            input_cate = call.data.replace('getproduct_','')
            UserOperations.purchase_a_products(call, input_cate)
            return
        
        if call.data.startswith("managecats_"):
            input_cate = call.data.replace('managecats_','')
            manage_categoriesbutton(call, input_cate)
            return
        
        logger.warning(f"Unknown callback data: {call.data}")
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        bot.send_message(call.message.chat.id, "An error occurred. Please try again.")


#Function to list Products
def is_product_command(message):
    """Check if message is a product command"""
    try:
        pattern = r'/\d{8}$'
        return bool(re.match(pattern, message))
    except Exception as e:
        logger.error(f"Error checking product command: {e}")
        return False
@bot.message_handler(content_types=["text"], func=lambda message: is_product_command(message.text))
def products_get(message):
    """Handle product selection"""
    try:
        UserOperations.purchase_a_products(message)
    except Exception as e:
        logger.error(f"Error processing product selection: {e}")
        bot.send_message(message.chat.id, "Error processing your request. Please try again.")
#Start command handler and function
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Home 🏘")
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        print(NOWPAYMENTS_API_KEY)
        1==1
        try:
            id = message.from_user.id
            usname = message.chat.username
            admins = GetDataFromDB.GetAdminIDsInDB()
            user_s = GetDataFromDB.AllUsers()
            for a_user_s in user_s:
                all_user_s = a_user_s[0]
            admin_s = GetDataFromDB.AllAdmins()
            for a_admin_s in admin_s:
                all_admin_s = a_admin_s[0]
            product_s = GetDataFromDB.AllProducts()
            for a_product_s in product_s:
                all_product_s = a_product_s[0]
            orders_s = GetDataFromDB.AllOrders()
            for a_orders_s in orders_s:
                all_orders_s = a_orders_s[0]
            
            keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboardadmin.row_width = 2
            
            # Guard clause: Handle empty admins list (first user becomes admin)
            if admins == []:
                users = GetDataFromDB.GetUserIDsInDB()
                if f"{id}" not in f"{users}":
                    CreateDatas.AddAuser(id,usname)
                user_type = "Shop Admin"
                CreateDatas.AddAdmin(id,usname)
                key0 = types.KeyboardButton(text="Manage Products 💼")
                key1 = types.KeyboardButton(text="Manage Categories 💼")
                key2 = types.KeyboardButton(text="Manage Orders 🛍")
                key3 = types.KeyboardButton(text="Payment Methods 💳")
                key4 = types.KeyboardButton(text="News To Users 📣")
                key5 = types.KeyboardButton(text="Switch To User 🙍‍♂️")
                keyboardadmin.add(key0)
                keyboardadmin.add(key1, key2)
                keyboardadmin.add(key3, key4)
                keyboardadmin.add(key5)
                store_statistics = f"➖➖➖Store's Statistics 📊➖➖➖\n\n\nTotal Users 🙍‍♂️: {all_user_s}\n\nTotal Admins 🤴: {all_admin_s}\n\nTotal Products 🏷: {all_product_s}\n\nTotal Orders 🛍: {all_orders_s}\n\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖"
                user_data = "0"
                bot.send_photo(chat_id=message.chat.id, photo="https://i.ibb.co/9vctwpJ/IMG-1235.jpg", caption=f"Dear {user_type},\n\nYour Wallet Balance: $ {user_data} 💰 \n\n{store_statistics}", reply_markup=keyboardadmin)
                return
            
            # Guard clause: Handle existing admin
            if f"{id}" in f"{admins}":
                keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                keyboardadmin.row_width = 2
                users = GetDataFromDB.GetUserIDsInDB()
                if f"{id}" not in f"{users}":
                    CreateDatas.AddAuser(id,usname)
                user_type = "Shop Admin"
                key0 = types.KeyboardButton(text="Manage Products 💼")
                key1 = types.KeyboardButton(text="Manage Categories 💼")
                key2 = types.KeyboardButton(text="Manage Orders 🛍")
                key3 = types.KeyboardButton(text="Payment Methods 💳")
                key4 = types.KeyboardButton(text="News To Users 📣")
                key5 = types.KeyboardButton(text="Switch To User 🙍‍♂️")
                keyboardadmin.add(key0)
                keyboardadmin.add(key1, key2)
                keyboardadmin.add(key3, key4)
                keyboardadmin.add(key5)

                store_statistics = f"➖➖➖Store's Statistics 📊➖➖➖\n\n\nTotal Users 🙍‍♂️: {all_user_s}\n\nTotal Admins 🤴: {all_admin_s}\n\nTotal Products 🏷: {all_product_s}\n\nTotal Orders 🛍: {all_orders_s}\n\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖"
                user_data = "0"
                bot.send_photo(chat_id=message.chat.id, photo="https://i.ibb.co/9vctwpJ/IMG-1235.jpg", caption=f"Dear {user_type},\n\nWelcome! 🤝\n\n{store_statistics}", reply_markup=keyboardadmin)
                return

            # Handle regular user
            users = GetDataFromDB.GetUserIDsInDB()
            if f"{id}" in f"{users}":
                user_type = "Customer"
                user_data = GetDataFromDB.GetUserWalletInDB(id)
            else:
                CreateDatas.AddAuser(id,usname)
                user_type = "Customer"
                user_data = GetDataFromDB.GetUserWalletInDB(id)
            bot.send_photo(chat_id=message.chat.id, photo="https://i.ibb.co/9vctwpJ/IMG-1235.jpg", caption=f"Dear {user_type},\n\nWelcome! 🤝\n\nBrowse our products, make purchases, and enjoy fast delivery! \nType /browse to start shopping. \n\n💬 Need help? \nContact our support team anytime.", reply_markup=keyboard)
        except Exception as e:
            print(e)
            admin_switch_user(message)
    except Exception as e:
        print(e)
        
#Switch admin to user handler
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Switch To User 🙍‍♂️")
def admin_switch_user(message):
    id = message.from_user.id
    usname = message.chat.username
    keyboard = create_user_keyboard()
    
    users = GetDataFromDB.GetUserIDsInDB()
    if f"{id}" not in f"{users}":
        CreateDatas.AddAuser(id,usname)
    
    user_type = "Customer"
    user_data = GetDataFromDB.GetUserWalletInDB(id)
    
    bot.send_photo(chat_id=message.chat.id, photo="https://i.ibb.co/9vctwpJ/IMG-1235.jpg", caption=f"Dear {user_type},\n\nYour Wallet Balance: $ {user_data} 💰 \n\nBrowse our products, make purchases, and enjoy fast delivery! \nType /browse to start shopping. \n\n💬 Need help? \nContact our support team anytime.", reply_markup=keyboard)
    bot.send_message(id, "You are on User Mode ✅\nSend /start command or press Home 🏘 button to switch back to Admin Mode", reply_markup=keyboard)

#Command handler to manage products
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Manage Products 💼")
def ManageProducts(message):
    id = message.from_user.id
    name = message.from_user.first_name
    usname = message.chat.username
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    key1 = types.KeyboardButton(text="Add New Product ➕")
    key2 = types.KeyboardButton(text="List Product 🏷")
    key3 = types.KeyboardButton(text="Delete Product 🗑️")
    key4 = types.KeyboardButton(text="Home 🏘")
    keyboardadmin.add(key1)
    keyboardadmin.add(key2, key3)
    keyboardadmin.add(key4)

    bot.send_message(id, "Choose an action to perform ✅", reply_markup=keyboardadmin)

#Command handler to add product
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Add New Product ➕")
def AddProductsMNG(message):
    id = message.from_user.id
    name = message.from_user.first_name
    usname = message.chat.username
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    msg = bot.send_message(id, "Reply With Your Product Name or Tittle: ✅")
    new_product_number = random.randint(10000000,99999999)
    productnumber = f"{new_product_number}"
    CreateDatas.AddProduct(productnumber, id, usname)
    global productnumbers
    productnumbers = productnumber
    bot.register_next_step_handler(msg, add_a_product_name)

#Function to add product name
def add_a_product_name(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    try:
        id = message.from_user.id
        productname = message.text
        msg = bot.send_message(id, "Reply With Your Product Description: ✅")
        CreateDatas.UpdateProductName(productname, productnumbers)
        bot.register_next_step_handler(msg, add_a_product_decription)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, add_a_product_name)

#Function to add product describtion
def add_a_product_decription(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    try:
        id = message.from_user.id
        description = message.text
        msg = bot.send_message(id, "Reply With Your Product Price: ✅")
        CreateDatas.UpdateProductDescription(description, productnumbers)
        bot.register_next_step_handler(msg, add_a_product_price)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, add_a_product_decription)

#Function to add product price
def add_a_product_price(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    try:
        id = message.from_user.id
        price = message.text
        msg = bot.send_message(id, "Attach Your Product Photo: ✅")
        CreateDatas.UpdateProductPrice(price, productnumbers)
        bot.register_next_step_handler(msg, add_a_product_photo_link)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, add_a_product_price)

#Function to add product photo
def add_a_product_photo_link(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    try:
        id = message.from_user.id
        image_link = message.photo[0].file_id
        all_categories = GetDataFromDB.GetCategoryIDsInDB()
        CreateDatas.UpdateProductproductimagelink(image_link, productnumbers)
        
        # Guard clause: Handle empty categories
        if all_categories == []:
            msg = bot.send_message(id, "Please reply with a new category's name")
            bot.register_next_step_handler(msg, add_a_product_category)
            return
        
        bot.send_message(id, f"CATEGORIES 👇")
        for catnum, catname in all_categories:
            bot.send_message(id, f"{catname} - ID: /{catnum} ✅")

        msg = bot.send_message(id, "Click on a Category ID to select Category for this Product: ✅\n\n⚠️Or Write A New Category", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, add_a_product_category)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, add_a_product_photo_link)

#Function to add product category
def add_a_product_category(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    id = message.from_user.id
    input_cat = message.text
    all_categories = GetDataFromDB.GetCategoryIDsInDB()
    input_cate = input_cat[1:99]

    categories = []
    for catnum, catname in all_categories:
        catnames = catname.upper()
        categories.append(catnames)
        
    def checkint():
        try:
            input_cat = int(input_cate)
            return input_cat
        except:
            return input_cate

    input_category = checkint() 
    if isinstance(input_category, int) == True:
        product_cate = GetDataFromDB.Get_A_CategoryName(input_category)
        product_category = product_cate.upper()
        if f"{product_category}" not in f"{categories}" or f"{product_category}" == "NONE":
            msg = bot.send_message(id, "Please reply with a new category's name", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, add_a_product_category)
            return
        
        # Existing category found
        msg = bot.send_message(id, "Attach Your Producy Keys In A Text File: ✅\n\n⚠️ Please Arrange Your Product Keys In the Text File, One Product Key Per Line In The File\n\n\n⚠️ Reply With Skip to skip this step if this Product has no Product Keys")
        CreateDatas.UpdateProductCategory(product_category, productnumbers)
        bot.register_next_step_handler(msg, add_a_product_keys_file)
        return
    
    # Create new category
    new_category_number = random.randint(1000,9999)
    input_cate = input_cat.upper()
    CreateDatas.AddCategory(new_category_number, input_cate)
    bot.send_message(id, f"New Category created successfully  - {input_cat}")
    msg = bot.send_message(id, "Attach Your Producy Keys In A Text File: ✅\n\n⚠️ Please Arrange Your Product Keys In the Text File, One Product Key Per Line In The File\n\n\n⚠️ Reply With Skip to skip this step if this Product has no Product Keys")
    CreateDatas.UpdateProductCategory(input_cate, productnumbers)
    bot.register_next_step_handler(msg, add_a_product_keys_file)

#Function to add product file for keys
def add_a_product_keys_file(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    try:
        id = message.from_user.id
        
        # Guard clause: Handle skip
        if message.text and message.text.upper() == "SKIP":
            msg = bot.send_message(id, "Reply With Download Link For This Product\n\nThis will be the Link customer will have access to after they have paid: ✅\n\n\n⚠️ Reply With Skip to skip this step if this Product has no Product Download Link")
            bot.register_next_step_handler(msg, add_a_product_download_link)
            return
        
        # Guard clause: Handle missing document
        if not message.document:
            msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
            bot.register_next_step_handler(msg, add_a_product_keys_file)
            return
        
        # Handle document upload
        keys_folder = "Keys"
        if not "Keys" in  os.listdir():
            try:
                os.mkdir("Keys")
            except Exception as e:
                print(e)
        else:
            pass
        KeysFiles = f"{keys_folder}/{productnumbers}.txt"
        file = message.document
        file_info = bot.get_file(file.file_id)
        file_path = file_info.file_path
        file_name = os.path.join(f"{KeysFiles}")
        downloaded_file = bot.download_file(file_path)
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, f'File f"{productnumbers}.txt" saved successfully.')
        CreateDatas.UpdateProductKeysFile(KeysFiles, productnumbers)
        quantity = open(file_name, 'r').read().splitlines()
        with open(file_name, 'r') as all:
            all_quantity = all.read()
        all_quantities = len(all_quantity.split('\n'))
        CreateDatas.UpdateProductQuantity(all_quantities, productnumbers)
        msg = bot.send_message(id, "Reply With Download Link For This Product\n\nThis will be the Link customer will have access to after they have paid: ✅\n\n\n⚠️ Reply With Skip to skip this step if this Product has no Product Download Link")
        bot.register_next_step_handler(msg, add_a_product_download_link)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, add_a_product_keys_file)

#Function to add product download link
def add_a_product_download_link(message):
    try:
        id = message.from_user.id
        download_link = message.text
        if message.text and message.text.upper() == "SKIP":
            bot.send_message(id, "Download Link Skipped ✅")
        else:
            CreateDatas.UpdateProductproductdownloadlink(download_link, productnumbers)
            CreateDatas.UpdateProductQuantity(int(100), productnumbers)
        
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        key1 = types.KeyboardButton(text="Add New Product ➕")
        key2 = types.KeyboardButton(text="List Product 🏷")
        key3 = types.KeyboardButton(text="Delete Product 🗑️")
        key4 = types.KeyboardButton(text="Home 🏘")
        keyboardadmin.add(key1)
        keyboardadmin.add(key2, key3)
        keyboardadmin.add(key4)
        productimage = GetDataFromDB.GetProductImageLink(productnumbers)
        productname = GetDataFromDB.GetProductName(productnumbers)
        productnumber = GetDataFromDB.GetProductNumber(productnumbers)
        productdescription = GetDataFromDB.GetProductDescription(productnumbers)
        productprice = GetDataFromDB.GetProductPrice(productnumbers)
        productquantity = GetDataFromDB.GetProductQuantity(productnumbers)
        captions = f"\n\n\nProduct Tittle: {productname}\n\n\nProduct Number: `{productnumber}`\n\n\nProduct Price: {productprice} {store_currency} 💰\n\n\nQuantity Avaialble: {productquantity} \n\n\nProduct Description: {productdescription}"
        bot.send_photo(chat_id=message.chat.id, photo=f"{productimage}", caption=f"{captions}", parse_mode='Markdown')
        bot.send_message(id, "Product Successfully Added ✅\n\nWhat will you like to do next ?", reply_markup=keyboardadmin)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, add_a_product_download_link)

#Command handler and functions to delete product
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Delete Product 🗑️")
def DeleteProductsMNG(message):
    try:
        id = message.from_user.id
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        productnumber_name = GetDataFromDB.GetProductNumberName()
        
        # Guard clause: Check admin permission
        if not is_admin(id, admins):
            bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
            return
        
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        
        # Guard clause: Handle no products
        if productnumber_name == []:
            msg = bot.send_message(id, "No product available, please send /start command to start creating products")
            bot.register_next_step_handler(msg, send_welcome)
            return
        
        bot.send_message(id, f"👇Product ID --- Product Name👇")
        for pid, tittle in productnumber_name:
            bot.send_message(id, f"/{pid} - `{tittle}`", parse_mode="Markdown")
        msg = bot.send_message(id, "Click on a Product ID of the product you want to delete: ✅", parse_mode="Markdown")
        bot.register_next_step_handler(msg, delete_a_product)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        pass
def delete_a_product(message):
    #try:
    id = message.from_user.id
    productnu = message.text
    productnumber = productnu[1:99]
    productnum = GetDataFromDB.GetProductIDs()
    productnums = []
    for productn in productnum:
        productnums.append(productn[0])
    print(productnums)
    
    # Guard clause: Check if product exists
    if int(productnumber) not in productnums:
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, delete_a_product)
        return
    
    try:
        global productnumbers
        productnumbers = productnumber
    except Exception as e:
        print(e)
    
    
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    key1 = types.KeyboardButton(text="Add New Product ➕")
    key2 = types.KeyboardButton(text="List Product 🏷")
    key3 = types.KeyboardButton(text="Delete Product 🗑️")
    key4 = types.KeyboardButton(text="Home 🏘")
    keyboardadmin.add(key1)
    keyboardadmin.add(key2, key3)
    keyboardadmin.add(key4)
    CleanData.delete_a_product(productnumber)
    msg = bot.send_message(id, "Deleted successfully 🗑️\n\n\nWhat will you like to do next ?\n\nSelect one of buttons 👇", reply_markup=keyboardadmin, parse_mode="Markdown")

#Command handler and fucntion to shop Items
@bot.message_handler(commands=['browse'])
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Shop Items 🛒")
def shop_items(message):
    UserOperations.shop_items(message)


# Dictionary to store Bitcoint payment data
bitcoin_payment_data = {}

# Function to get BTC amount for the given fiat amount
def get_btc_amount(fiat_amount, currency):
    url = f'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={currency.lower()}'
    response = requests.get(url)
    if response.status_code == 200:
        price = response.json()['bitcoin'][currency.lower()]
        btc_amount = int(fiat_amount) / int(price)
        return btc_amount
    else:
        print(f"Error fetching BTC price: {response.status_code} - {response.text}")
        return None

# Function to create a new payment
def create_payment_address(btc_amount):
    url = 'https://api.nowpayments.io/v1/payment'
    headers = {
        'x-api-key': NOWPAYMENTS_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'price_amount': btc_amount,
        'price_currency': 'btc',
        'pay_currency': 'btc',
        'ipn_callback_url': 'https://api.nowpayments.io/ipn',
        'order_id': '5555555555',
        'order_description': 'Payment for Order'
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        return response.json()['pay_address'], response.json()['payment_id']
    else:
        print(f"Error creating payment address: {response.status_code} - {response.text}")
        return None, None
    
# Function to check the payment status
def check_payment_status(payment_id):
    url = f'https://api.nowpayments.io/v1/payment/{payment_id}'
    headers = {
        'x-api-key': NOWPAYMENTS_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['payment_status']
    else:
        print(f"Error checking payment status: {response.status_code} - {response.text}")
        return None


# Command handler to pay with Bitcoin
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Bitcoin ฿")
def bitcoin_pay_command(message):
    id = message.from_user.id
    username = message.from_user.username
    
    
    order_info = UserOperations.orderdata()
    new_order = order_info
    new_orders = order_info
    
    # Guard clause: Handle no order
    if f"{order_info}" == "None":
        bot.send_message(id, "No order found !", reply_markup=keyboard, parse_mode="Markdown")
        return
    
    # Guard clause: Handle sold out
    if int(f"{order_info[6]}") < int(1):
        bot.send_message(id, "This Item is soldout !!!", reply_markup=keyboard, parse_mode="Markdown")
        return
    
    try:
        fiat_amount = new_order[2]
        btc_amount = get_btc_amount(fiat_amount, store_currency)
        
        # Guard clause: Handle BTC conversion error
        if not btc_amount:
            bot.send_message(message.chat.id, "Error converting amount to BTC. Please try again later.")
            return
        
        payment_address, payment_id = create_payment_address(btc_amount)
        
        # Guard clause: Handle payment address creation error
        if not payment_address or not payment_id:
            bot.send_message(message.chat.id, "Error creating payment address. Please try again later.\n\nOR Amount value is too small")
            return
        
        try:
            now = datetime.now()
            orderdate = now.strftime("%Y-%m-%d %H:%M:%S")
            ordernumber = random.randint(10000,99999)
            paidmethod = "NO"
            add_key = "NIL"
            productdownloadlink = GetDataFromDB.GetProductDownloadLink(new_orders[0])

            CreateDatas.AddOrder(id, username,new_orders[1], new_orders[2], orderdate, paidmethod, productdownloadlink, add_key, ordernumber, new_orders[0], payment_id)
        except Exception as e:
            print(e)
            pass
        keyboard2 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard2.row_width = 2
        key1 = types.KeyboardButton(text="Check Payment Status ⌛")
        keyboard2.add(key1)
        bot.send_message(id, f"Please send extact {btc_amount:.8f} BTC (approximately {fiat_amount} {store_currency}) to the following Bitcoin", reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id, f"Address: `{payment_address}`", reply_markup=keyboard2, parse_mode='Markdown')
        bot.send_message(message.chat.id, f"Please stay on this page and click on Check Payment Status ⌛ button until payment is confirmed", reply_markup=keyboard2, parse_mode='Markdown')

    except (IndexError, ValueError):
        bot.send_message(message.chat.id, f"Invalid command.")

# Command handler and function to Check bitcoin payment status
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Check Payment Status ⌛")
def bitcoin_check_command(message):
    id = message.from_user.id
    orders = GetDataFromDB.GetAllUnfirmedOrdersUser(id)
    
    # Guard clause: Handle no orders
    if orders == [] or orders == "None":
        bot.send_message(message.chat.id, "No order found !")
        return
    
    for ordernumber, productname, buyerusername, payment_id, productnumber in orders:
        status = check_payment_status(payment_id)
        
        # Guard clause: Handle no status
        if not status:
            bot.send_message(message.chat.id, f"No order found with pending payment confirmation !")
            continue
        
        # Guard clause: Handle non-finished status
        if status != 'finished':
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            keyboard.row_width = 2
            key1 = types.KeyboardButton(text="Check Payment Status ⌛")
            key2 = types.KeyboardButton(text="Home 🏘")
            keyboard.add(key1)
            keyboard.add(key2)
            bot.send_message(message.chat.id, f"Your payment is {status} for Order ID: {ordernumber}", reply_markup=keyboard)
            continue
        
        # Handle finished payment
        try:
            keys_folder = 'Keys'
            keys_location = f"{keys_folder}/{productnumber}.txt"
            all_key = open(f"{keys_location}", 'r').read().splitlines()
            def keeys():
                if all_key == []:
                    return "NIL"
                else:
                    return all_key
            all_keys = keeys()
            for a_key in all_keys:
                1==1
            productkeys = a_key

            name_file = keys_location
            with open(f'{name_file}', 'r') as file:
                lines = file.readlines()
            with open(f'{name_file}', 'w') as file:
                for line in lines:
                    if f"{productkeys}" not in line:
                        file.write(line)
                file.truncate()
        except:
            pass
    
        def check_if_keys():
            try:
                return productkeys
            except:
                return "NIL"

        add_key = check_if_keys()

        bot.send_message(message.chat.id, "Payment received and confirmed!")
        CreateDatas.UpdateOrderPurchasedKeys(add_key, ordernumber)
        CreateDatas.UpdateOrderPaymentMethod("Bitcoin", ordernumber)
        product_list = GetDataFromDB.GetProductInfoByPName(productnumber)
        for productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory in product_list:
            list_m =  [productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory]
        new_quantity = int(f"{productquantity}") - int(1)
        CreateDatas.UpdateProductQuantity(int(new_quantity), productnumber)
        msg = bot.send_message(message.chat.id, "Payment successful ✅")
        msg = bot.send_message(message.chat.id, "Would you like to write a note to the Seller ?")
        msg = bot.send_message(message.chat.id, "Reply with your note or reply with NIL to proceed")
        global order_number
        order_number = ordernumber
        bot.register_next_step_handler(msg, complete_order)
        
    bot.send_message(message.chat.id, "Done ✅")

def complete_order(message):
    id = message.from_user.id
    input_commend = message.text
    CreateDatas.UpdateOrderComment(input_commend, order_number)
    order_details = GetDataFromDB.GetOrderDetails(order_number)
    for buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, buyercomment, ordernumber, productnumber in order_details:
        print(f"{order_details}")
    bot.send_message(message.chat.id, "Thank for your order 🤝")
    msg = f"YOUR NEW ORDER ✅\n\n\nOrder 🆔: {ordernumber}\nOrder Date 🗓: {orderdate}\nProduct Name 📦: {productname}\nProduct 🆔:{productnumber}\nProduct Price 💰: {productprice} {store_currency}\nPayment Method 💳: {paidmethod}\nProduct Keys 🔑: {productkeys}\nDownload ⤵️: {productdownloadlink}"
    bot.send_message(id, text=f"{msg}", reply_markup=keyboard)
    admin_id = GetDataFromDB.GetProduct_A_AdminID(productnumber)
    bot.send_message(admin_id, text=f"{msg}", reply_markup=keyboard)

#Command handler and function to List My Orders 🛍
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "My Orders 🛍")
def MyOrdersList(message):
    id = message.from_user.id
    
    
    my_orders = GetDataFromDB.GetOrderIDs_Buyer(id)
    
    # Guard clause: Handle no orders
    if my_orders == [] or my_orders == "None":
        bot.send_message(id, "You have not completed any order yet, please purchase an Item now", reply_markup=keyboard)
        return
    
    for my_order in my_orders:
        order_details = GetDataFromDB.GetOrderDetails(my_order[0])
        for buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, buyercomment, ordernumber, productnumber in order_details:
            msg = f"{productname} ORDERED ON {orderdate} ✅\n\n\nOrder 🆔: {ordernumber}\nOrder Date 🗓: {orderdate}\nProduct Name 📦: {productname}\nProduct 🆔:{productnumber}\nProduct Price 💰: {productprice} {store_currency}\nPayment Method 💳: {paidmethod}\nProduct Keys 🔑: {productkeys}\nDownload ⤵️: {productdownloadlink}"
            bot.send_message(id, text=f"{msg}")
    bot.send_message(id, "List completed ✅", reply_markup=keyboard)

#Command handler and function to list Store Supports 📞
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Support 📞")
def ContactSupport(message):
    id = message.from_user.id
    admin_usernames = GetDataFromDB.GetAdminUsernamesInDB()
    for usernames in admin_usernames:
        bot.send_message(id, f"Contact us @{usernames[0]}", reply_markup=keyboard)

#Command handler and function to add New Category
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Add New Category ➕")
def AddNewCategoryMNG(message):
    try:
        id = message.from_user.id
        admins = GetDataFromDB.GetAdminIDsInDB()
        
        # Guard clause: Check admin permission
        if not is_admin(id, admins):
            bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
            return
        
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        msg = bot.send_message(id, "Reply with name you want to name your new category", reply_markup=keyboard)
        bot.register_next_step_handler(msg, manage_categories)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, AddNewCategoryMNG)

#Command handler and function to List Category
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "List Categories 🏷")
def ListCategoryMNG(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    try:
        id = message.from_user.id
        all_categories = GetDataFromDB.GetCategoryIDsInDB()
        key1 = types.KeyboardButton(text="Add New Category ➕")
        key2 = types.KeyboardButton(text="List Categories 🏷")
        key3 = types.KeyboardButton(text="Edit Category Name ✏️")
        key4 = types.KeyboardButton(text="Delete Category 🗑️")
        key5 = types.KeyboardButton(text="Home 🏘")
        keyboardadmin.add(key1, key2)
        keyboardadmin.add(key3, key4)
        keyboardadmin.add(key5)
        
        # Guard clause: Handle no categories
        if all_categories == []:
            msg = bot.send_message(id, "No Category in your Store !!!", reply_markup=keyboardadmin)
            return
        
        keyboardadmin = types.InlineKeyboardMarkup()
        for catnum, catname in all_categories:
            text_but = f"🏷 {catname}"
            text_cal = f"listcats_{catnum}"
            keyboardadmin.add(types.InlineKeyboardButton(text=text_but, callback_data=text_cal))
        bot.send_message(id, f"CATEGORIES:", reply_markup=keyboardadmin)
        bot.send_message(id, "List completed ✅")
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, ManageCategoryMNG)

#Command handler and function to Delete Category
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Delete Category 🗑️")
def AddNewCategoryMNG(message):
    try:
        id = message.from_user.id
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        
        # Guard clause: Check admin permission
        if not is_admin(id, admins):
            bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
            return
        
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        key1 = types.KeyboardButton(text="Home 🏘")
        keyboardadmin.add(key1)
        try:
            nen_category_name = "Deleted"
            try:
                CreateDatas.Update_All_ProductCategory(nen_category_name, product_cate)
            except Exception as e:
                print(e)
            product_cate = GetDataFromDB.Get_A_CategoryName(category_number)
            msg = bot.send_message(id, f"{product_cate} successfully deleted 🗑️", reply_markup=keyboardadmin)
            CleanData.delete_a_category(category_number)
            bot.register_next_step_handler(msg, send_welcome)

        except:
            msg = bot.send_message(id, "Category not found !!!", reply_markup=keyboardadmin)
            bot.register_next_step_handler(msg, send_welcome)

    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, AddNewCategoryMNG)

#Command handler and functions to Edit Category Name
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Edit Category Name ✏️")
def EditCategoryNameMNG(message):
    try:
        id = message.from_user.id
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        
        # Guard clause: Check admin permission
        if not is_admin(id, admins):
            bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
            return
        
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        key1 = types.KeyboardButton(text="Add New Category ➕")
        key2 = types.KeyboardButton(text="List Categories 🏷")
        key3 = types.KeyboardButton(text="Edit Category Name ✏️")
        key4 = types.KeyboardButton(text="Delete Category 🗑️")
        key5 = types.KeyboardButton(text="Home 🏘")
        keyboardadmin.add(key1, key2)
        keyboardadmin.add(key3, key4)
        keyboardadmin.add(key5)
        try:
            product_cate = GetDataFromDB.Get_A_CategoryName(category_number)
            msg = bot.send_message(id, f"Current Category's Name: {product_cate} \n\n\nReply with your new Category's name")
            bot.register_next_step_handler(msg, edit_a_category_name)
        except:
            msg = bot.send_message(id, "Category to edit not found !!!", reply_markup=keyboardadmin)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, EditCategoryNameMNG)
def edit_a_category_name(message):
    try:
        id = message.from_user.id
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        
        # Guard clause: Check admin permission
        if not is_admin(id, admins):
            bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
            return
        
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        key1 = types.KeyboardButton(text="Home 🏘")
        keyboardadmin.add(key1)
        try:
            nen_category_n = message.text
            nen_category_name = nen_category_n.upper()
            product_cate = GetDataFromDB.Get_A_CategoryName(category_number)
            try:
                CreateDatas.Update_All_ProductCategory(nen_category_name, product_cate)
            except Exception as e:
                print(e)
            CreateDatas.Update_A_Category(nen_category_name, category_number)
            msg = bot.send_message(id, "Category's name successfully updated: ✅", reply_markup=keyboardadmin)
            bot.register_next_step_handler(msg, send_welcome)

        except:
            msg = bot.send_message(id, "Category not found !!!", reply_markup=keyboardadmin)
            bot.register_next_step_handler(msg, send_welcome)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, AddNewCategoryMNG)

#Command handler and function to Manage Category
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Manage Categories 💼")
def ManageCategoryMNG(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    try:
        id = message.from_user.id
        all_categories = GetDataFromDB.GetCategoryIDsInDB()
        
        # Guard clause: Handle no categories
        if all_categories == []:
            msg = bot.send_message(id, "No Category in your Store !!!\n\n\nPlease reply with a new category's name to create Category")
            bot.register_next_step_handler(msg, manage_categories)
            return
        
        keyboardadmin = types.InlineKeyboardMarkup()
        for catnum, catname in all_categories:
            text_but = f"🏷 {catname}"
            text_cal = f"managecats_{catnum}"
            keyboardadmin.add(types.InlineKeyboardButton(text=text_but, callback_data=text_cal))
        bot.send_message(id, f"CATEGORIES:", reply_markup=keyboardadmin)
        
        keyboard1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard1.row_width = 2
        key1 = types.KeyboardButton(text="Add New Category ➕")
        key2 = types.KeyboardButton(text="Home 🏘")
        keyboard1.add(key1)
        keyboard1.add(key2)
        msg = bot.send_message(id, "Select Category you want to manage: ✅\n\nOr Create new Category", reply_markup=keyboard1)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, ManageCategoryMNG)

def manage_categories(message):
    global category_number
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    input_cat = message.text
    all_categories = GetDataFromDB.GetCategoryIDsInDB()
    input_cate = input_cat
    categories = []
    for catnum, catname in all_categories:
        catnames = catname.upper()
        categories.append(catnames)

    def checkint():
        try:
            input_cat = int(input_cate)
            return input_cat
        except:
            return input_cate

    input_category = checkint() 
    if isinstance(input_category, int) == True:
        product_cate = GetDataFromDB.Get_A_CategoryName(input_category)
        product_category = product_cate.upper()
        if f"{product_category}" not in f"{categories}" or f"{product_category}" == "NONE":
            msg = bot.send_message(id, "Category not found !!!\n\n\nPlease reply with a new category's name to create category")
            bot.register_next_step_handler(msg, manage_categories)
            return
        
        # Existing category found
        category_num = input_cate
        key1 = types.KeyboardButton(text="Add New Category ➕")
        key2 = types.KeyboardButton(text="List Categories 🏷")
        key3 = types.KeyboardButton(text="Edit Category Name ✏️")
        key4 = types.KeyboardButton(text="Delete Category 🗑️")
        key5 = types.KeyboardButton(text="Home 🏘")
        keyboardadmin.add(key1, key2)
        keyboardadmin.add(key3, key4)
        keyboardadmin.add(key5)
        bot.send_message(id, f"What will you like to do next ?", reply_markup=keyboardadmin)
        category_number = category_num
        return
    
    # Create new category
    new_category_number = random.randint(1000,9999)
    input_cate = input_cat.upper()
    CreateDatas.AddCategory(new_category_number, input_cate)
    key1 = types.KeyboardButton(text="Add New Category ➕")
    key2 = types.KeyboardButton(text="Manage Categories 💼")
    key3 = types.KeyboardButton(text="Home 🏘")
    keyboardadmin.add(key1)
    keyboardadmin.add(key2)
    keyboardadmin.add(key3)
    bot.send_message(id, f"New Category {input_cat} created successfully\n\n\nWhat will you like to do next ?", reply_markup=keyboardadmin)
    category_num = new_category_number
    category_number = category_num

def manage_categoriesbutton(message, input_c):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    id = message.from_user.id
    all_categories = GetDataFromDB.GetCategoryIDsInDB()
    input_cate = input_c
    categories = []
    for catnum, catname in all_categories:
        catnames = catname.upper()
        categories.append(catnames)
    input_category = input_cate
    product_cate = GetDataFromDB.Get_A_CategoryName(input_category)
    product_category = product_cate.upper()
    if f"{product_category}" not in f"{categories}" or f"{product_category}" == "NONE":
        msg = bot.send_message(id, "Category not found !!!\n\n\nPlease reply with a new category's name to create category")
        bot.register_next_step_handler(msg, manage_categoriesbutton)
        return
    
    # Existing category found
    category_num = input_cate
    key1 = types.KeyboardButton(text="Add New Category ➕")
    key2 = types.KeyboardButton(text="List Categories 🏷")
    key3 = types.KeyboardButton(text="Edit Category Name ✏️")
    key4 = types.KeyboardButton(text="Delete Category 🗑️")
    key5 = types.KeyboardButton(text="Home 🏘")
    keyboardadmin.add(key1, key2)
    keyboardadmin.add(key3, key4)
    keyboardadmin.add(key5)
    bot.send_message(id, f"What will you like to do next ?", reply_markup=keyboardadmin)
        
    global category_number
    category_number = category_num
    print(category_number)

#Command handler and function to List Product
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "List Product 🏷")
def LISTProductsMNG(message):
    id = message.from_user.id
    keyboarda = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboarda.row_width = 2
    admins = GetDataFromDB.GetAdminIDsInDB()
    productinfos = GetDataFromDB.GetProductInfos()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    
    # Guard clause: Handle no products
    if productinfos == []:
        msg = bot.send_message(id, "No product available, please send /start command to start creating products")
        bot.register_next_step_handler(msg, send_welcome)
        return
    
    keyboard = types.InlineKeyboardMarkup()
    for pid, tittle, price in productinfos:
        text_but = f"💼 {tittle} - {price} {store_currency}"
        text_cal = f"getproductig_{pid}"
        keyboard.add(types.InlineKeyboardButton(text=text_but, callback_data=text_cal))
    bot.send_message(id, f"PRODUCTS:", reply_markup=keyboard)
    key1 = types.KeyboardButton(text="Add New Product ➕")
    key2 = types.KeyboardButton(text="List Product 🏷")
    key3 = types.KeyboardButton(text="Delete Product 🗑️")
    key4 = types.KeyboardButton(text="Home 🏘")
    keyboarda.add(key1)
    keyboarda.add(key2, key3)
    keyboarda.add(key4)
    msg = bot.send_message(id, "List Finished: ✅", reply_markup=keyboarda, parse_mode="Markdown")

#Command handler and functions to  Message All Store Users
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "News To Users 📣")
def MessageAllUsers(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    msg = bot.send_message(id, f"This Bot is about to Broadcast mesage to all Shop Users\n\n\nReply with the message you want to Broadcast: ✅")
    bot.register_next_step_handler(msg, message_all_users)
def message_all_users(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    try:
        key1 = types.KeyboardButton(text="Manage Products 💼")
        key2 = types.KeyboardButton(text="Manage Orders 🛍")
        key3 = types.KeyboardButton(text="Payment Methods 💳")
        key4 = types.KeyboardButton(text="News To Users 📣")
        key5 = types.KeyboardButton(text="Switch To User 🙍‍♂️")
        keyboardadmin.add(key1, key2)
        keyboardadmin.add(key3, key4)
        keyboardadmin.add(key5)
        input_message = message.text
        all_users = GetDataFromDB.GetUsersInfo()
        
        # Guard clause: Handle no users
        if all_users == []:
            msg = bot.send_message(id, "No user available in your store, /start", reply_markup=keyboardadmin)
            return
        
        bot.send_message(id, "Now Broadcasting Message To All Users: ✅")
        for uid, uname, uwallet in all_users:
            try:
                bot.send_message(uid, f"{input_message}")
                bot.send_message(id, f"Message successfully sent ✅ To: @`{uname}`")
                time.sleep(0.5)
            except:
                bot.send_message(id, f"User @{uid} has blocked the bot - {uname} ")
        bot.send_message(id, f"Broadcast Completed ✅", reply_markup=keyboardadmin)
    except Exception as e:
        print(e)
        bot.send_message(id, "Error 404 🚫, try again with corrected input.")


#Command handler and function to Manage Orders
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Manage Orders 🛍")
def ManageOrders(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    key1 = types.KeyboardButton(text="List Orders 🛍")
    key2 = types.KeyboardButton(text="Delete Order 🗑️")
    key3 = types.KeyboardButton(text="Home 🏘")
    keyboardadmin.add(key1)
    keyboardadmin.add(key2, key3)
    bot.send_message(id, "Choose an action to perform ✅", reply_markup=keyboardadmin)

#Command handler and function to List All Orders
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "List Orders 🛍")
def ListOrders(message):
    try:
        id = message.from_user.id
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        all_orders = GetDataFromDB.GetOrderInfo()
        
        # Guard clause: Check admin permission
        if not is_admin(id, admins):
            bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
            return
        
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        
        # Guard clause: Handle no orders
        if all_orders == []:
            bot.send_message(id, "No Order available in your store, /start")
            return
        
        bot.send_message(id, "Your Oders List: ✅")
        bot.send_message(id, f"👇 OrderID - ProductName - BuyerUserName👇")
        for ordernumber, productname, buyerusername in all_orders:
            import time
            time.sleep(0.5)
            bot.send_message(id, f"`{ordernumber}` - `{productname}` - @{buyerusername}")
        key1 = types.KeyboardButton(text="List Orders 🛍")
        key2 = types.KeyboardButton(text="Delete Order 🗑️")
        key3 = types.KeyboardButton(text="Home 🏘")
        keyboardadmin.add(key1)
        keyboardadmin.add(key2, key3)
        bot.send_message(id, f"List Completed ✅", reply_markup=keyboardadmin)
    except Exception as e:
        print(e)
        bot.send_message(id, "Error 404 🚫, try again with corrected input.")


#Command handler and functions to Delete Order
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Delete Order 🗑️")
def DeleteOrderMNG(message):
    try:
        id = message.from_user.id
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        all_orders = GetDataFromDB.GetOrderInfo()
        
        # Guard clause: Check admin permission
        if not is_admin(id, admins):
            bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
            return
        
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        
        # Guard clause: Handle no orders
        if all_orders == []:
            key1 = types.KeyboardButton(text="List Orders 🛍")
            key2 = types.KeyboardButton(text="Home 🏘")
            keyboardadmin.add(key1)
            keyboardadmin.add(key2)
            bot.send_message(id, "No Order available in your store, /start", reply_markup=keyboardadmin)
            return
        
        bot.send_message(id, f"👇 OrderID - ProductName - BuyerUserName 👇")
        for ordernumber, productname, buyerusername in all_orders:
            bot.send_message(id, f"/{ordernumber} - `{productname}` - @{buyerusername}", parse_mode="Markdown")
        msg = bot.send_message(id, "Click on an Order ID of the order you want to delete: ✅", parse_mode="Markdown")
        bot.register_next_step_handler(msg, delete_an_order)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, DeleteOrderMNG)
def delete_an_order(message):
    try:
        id = message.from_user.id
        ordernu = message.text
        ordernumber = ordernu[1:99]
        ordernum = GetDataFromDB.GetOrderIDs()
        ordernumbers = []
        for ordern in ordernum:
            ordernumbers.append(ordern[0])
        
        # Guard clause: Check if order exists
        if f"{ordernumber}" not in f"{ordernumbers}":
            msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
            bot.register_next_step_handler(msg, delete_an_order)
            return
        
        try:
            global ordernums
            ordernums = ordernumber
        except Exception as e:
            print(e)
        
        
        admins = GetDataFromDB.GetAdminIDsInDB()
        
        # Guard clause: Check admin permission
        if not is_admin(id, admins):
            bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
            return
        
        keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboardadmin.row_width = 2
        key1 = types.KeyboardButton(text="List Orders 🛍")
        key2 = types.KeyboardButton(text="Home 🏘")
        keyboardadmin.add(key1)
        keyboardadmin.add(key2)
        CleanData.delete_an_order(ordernumber)
        msg = bot.send_message(id, "Deleted successfully 🗑️\n\n\nWhat will you like to do next ?\n\nSelect one of buttons 👇", reply_markup=keyboardadmin, parse_mode="Markdown")
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, delete_an_order)

#Command handler and function to Manage Payment Methods
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Payment Methods 💳")
def PaymentMethodMNG(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    key1 = types.KeyboardButton(text="Add Bitcoin Method ➕")
    key2 = types.KeyboardButton(text="Home 🏘")
    keyboardadmin.add(key1)
    keyboardadmin.add(key2)
    bot.send_message(id, "Choose an action to perform ✅", reply_markup=keyboardadmin)


#Command handler and function to Add API Keys for Bitcoin Payment Method
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Add Bitcoin Method ➕")
def AddBitcoinAPIKey(message):
    id = message.from_user.id
    username = message.from_user.username
    admins = GetDataFromDB.GetAdminIDsInDB()
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    edit_methods = "Bitcoin"
    global edit_method
    edit_method = edit_methods
    all_pay_methods = GetDataFromDB.GetPaymentMethodsAll(edit_method)
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return

    if f"{edit_method}" in f"{all_pay_methods}":
        bot.send_message(id, f"{edit_method} Payment method is already added ✅", reply_markup=keyboardadmin)
        return
    
    CreateDatas.AddPaymentMethod(id, username, edit_method)

    try:
        for method_name, token_clientid_keys, sectret_keys in all_pay_methods:
            all = method_name, token_clientid_keys, sectret_keys
        msg = bot.send_message(id, f"Reply With Your {edit_method} API Key for your NowPayments Account (https://account.nowpayments.io/create-account?link_id=3539852335): ✅")
        bot.register_next_step_handler(msg, add_bitcoin_api_key)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, AddBitcoinAPIKey)
def add_bitcoin_api_key(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    try:
        key1 = types.KeyboardButton(text="Home 🏘")
        keyboardadmin.add(key1)
        id = message.from_user.id
        api_key = message.text
        username = message.from_user.username
        CreateDatas.UpdatePaymentMethodToken(id, username, api_key, edit_method)
        bot.send_message(id, "Bitcoin Added successfully ✅", reply_markup=keyboardadmin)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, AddBitcoinAPIKey)

#Command handler and function to Add API Secret Key for Bitcoin Payment Method
@bot.message_handler(content_types=["text"], func=lambda message: message.text == "Add Bitcoin Secret ➕")
def AddBitcoinSecretKey(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    all_pay_methods = GetDataFromDB.GetPaymentMethodsAll(edit_method)
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboardadmin)
        return
    
    try:
        for method_name, token_clientid_keys, sectret_keys in all_pay_methods:
            all = method_name, token_clientid_keys, sectret_keys
        msg = bot.send_message(id, f"Reply With Your {edit_method} API Key for your NowPayments Account (https://account.nowpayments.io/create-account?link_id=3539852335): ✅")
        bot.register_next_step_handler(msg, add_bitcoin_secret_key)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, AddBitcoinSecretKey)
def add_bitcoin_secret_key(message):
    id = message.from_user.id
    admins = GetDataFromDB.GetAdminIDsInDB()
    keyboardadmin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboardadmin.row_width = 2
    
    # Guard clause: Check admin permission
    if not is_admin(id, admins):
        bot.send_message(id, "⚠️ Only Admin can use this command !!!", reply_markup=keyboard)
        return
    
    try:
        key1 = types.KeyboardButton(text="Home 🏘")
        keyboardadmin.add(key1)
        id = message.from_user.id
        api_key = message.text
        username = message.from_user.username
        CreateDatas.UpdatePaymentMethodSecret(id, username, api_key, edit_method)
        bot.send_message(id, "Added successfully ✅", reply_markup=keyboardadmin)
    except Exception as e:
        print(e)
        msg = bot.send_message(id, "Error 404 🚫, try again with corrected input.")
        bot.register_next_step_handler(msg, AddBitcoinSecretKey)

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        flask_app.run(debug=False, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Error starting Flask application: {e}")
        exit(1)
