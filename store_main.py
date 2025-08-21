# -*- coding: utf-8 -*-
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
from telebot.types import LabeledPrice, PreCheckoutQuery, SuccessfulPayment, ShippingOption
import json
from dotenv import load_dotenv
import psycopg2

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

# Load environment variables
load_dotenv('config.env')

# Bot instance
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'), threaded=False)
store_currency = os.getenv('STORE_CURRENCY', 'USD')

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
logger.info(f"DATABASE_URL: {DATABASE_URL}")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please set it in your Render environment.")

def get_db_connection():
    """Establish and return a database connection"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

class DBManager:
    @staticmethod
    def initialize_database():
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id BIGINT PRIMARY KEY,
                        usname VARCHAR(255),
                        wallet INTEGER DEFAULT 0,
                        language VARCHAR(5) DEFAULT 'en'
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS admins (
                        id BIGINT PRIMARY KEY,
                        usname VARCHAR(255)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        productnumber BIGINT PRIMARY KEY,
                        adminid BIGINT,
                        adminusname VARCHAR(255),
                        productname VARCHAR(255),
                        productdescription TEXT,
                        productprice NUMERIC(10, 2),
                        productimagelink TEXT,
                        productcategory VARCHAR(255),
                        productkeysfile TEXT,
                        productquantity INTEGER,
                        productdownloadlink TEXT
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        ordernumber BIGINT PRIMARY KEY,
                        buyerid BIGINT,
                        buyerusername VARCHAR(255),
                        productname VARCHAR(255),
                        productprice NUMERIC(10, 2),
                        orderdate TIMESTAMP,
                        paidmethod VARCHAR(255),
                        productdownloadlink TEXT,
                        productkeys TEXT,
                        productnumber BIGINT,
                        payment_id VARCHAR(255),
                        buyercomment TEXT
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS categories (
                        categorynumber BIGINT PRIMARY KEY,
                        categoryname VARCHAR(255)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS paymentmethods (
                        methodname VARCHAR(255) PRIMARY KEY,
                        adminid BIGINT,
                        adminusname VARCHAR(255),
                        token_clientid_keys TEXT,
                        sectret_keys TEXT
                    );
                """)
                conn.commit()
                logger.info("Database tables initialized successfully.")
            except psycopg2.Error as e:
                logger.error(f"Error initializing database tables: {e}")
                conn.rollback()
            finally:
                cur.close()
                conn.close()

DBManager.initialize_database()

class CreateDatas:
    @staticmethod
    def AddAuser(id,usname):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (id, usname, wallet, language) VALUES (%s, %s, %s, %s)", (id, usname, 0, 'en'))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def update_user_language(user_id, language_code):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET language = %s WHERE id = %s", (language_code, user_id))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def AddAdmin(id,usname):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO admins (id, usname) VALUES (%s, %s)", (id, usname))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def AddProduct(productnumber, id, usname):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO products (productnumber, adminid, adminusname) VALUES (%s, %s, %s)", (productnumber, id, usname))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductName(productname, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productname = %s WHERE productnumber = %s", (productname, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductDescription(description, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productdescription = %s WHERE productnumber = %s", (description, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductPrice(price, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productprice = %s WHERE productnumber = %s", (price, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductproductimagelink(imagelink, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productimagelink = %s WHERE productnumber = %s", (imagelink, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductCategory(category, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productcategory = %s WHERE productnumber = %s", (category, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductKeysFile(keysfile, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productkeysfile = %s WHERE productnumber = %s", (keysfile, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductQuantity(quantity, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productquantity = %s WHERE productnumber = %s", (quantity, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductproductdownloadlink(downloadlink, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productdownloadlink = %s WHERE productnumber = %s", (downloadlink, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def AddCategory(categorynumber, categoryname):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO categories (categorynumber, categoryname) VALUES (%s, %s)", (categorynumber, categoryname))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def Update_A_Category(categoryname, categorynumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE categories SET categoryname = %s WHERE categorynumber = %s", (categoryname, categorynumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def Update_All_ProductCategory(newcategoryname, oldcategoryname):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productcategory = %s WHERE productcategory = %s", (newcategoryname, oldcategoryname))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def AddOrder(buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, ordernumber, productnumber, payment_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO orders (buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, ordernumber, productnumber, payment_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, ordernumber, productnumber, payment_id))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateOrderPaymentMethod(paidmethod, ordernumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE orders SET paidmethod = %s WHERE ordernumber = %s", (paidmethod, ordernumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateOrderPurchasedKeys(productkeys, ordernumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE orders SET productkeys = %s WHERE ordernumber = %s", (productkeys, ordernumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateOrderComment(comment, ordernumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE orders SET buyercomment = %s WHERE ordernumber = %s", (comment, ordernumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def AddPaymentMethod(adminid, adminusname, methodname):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO paymentmethods (adminid, adminusname, methodname) VALUES (%s, %s, %s)", (adminid, adminusname, methodname))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdatePaymentMethodToken(adminid, adminusname, token, methodname):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE paymentmethods SET token_clientid_keys = %s WHERE methodname = %s", (token, methodname))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdatePaymentMethodSecret(adminid, adminusname, secret, methodname):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE paymentmethods SET sectret_keys = %s WHERE methodname = %s", (secret, methodname))
        conn.commit()
        cur.close()
        conn.close()

class GetDataFromDB:
    @staticmethod
    def get_language_for_user(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT language FROM users WHERE id = %s", (user_id,))
        language = cur.fetchone()
        cur.close()
        conn.close()
        if language:
            return language[0]
        return 'en'

    @staticmethod
    def GetUserIDsInDB():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users")
        user_ids = cur.fetchall()
        cur.close()
        conn.close()
        return user_ids


    @staticmethod
    def GetAdminIDsInDB():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM admins")
        admin_ids = cur.fetchall()
        cur.close()
        conn.close()
        return admin_ids

    @staticmethod
    def AllUsers():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(id) FROM users")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return users

    @staticmethod
    def AllAdmins():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(id) FROM admins")
        admins = cur.fetchall()
        cur.close()
        conn.close()
        return admins

    @staticmethod
    def AllProducts():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(productnumber) FROM products")
        products = cur.fetchall()
        cur.close()
        conn.close()
        return products

    @staticmethod
    def AllOrders():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(ordernumber) FROM orders")
        orders = cur.fetchall()
        cur.close()
        conn.close()
        return orders

    @staticmethod
    def GetUserWalletInDB(id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT wallet FROM users WHERE id = %s", (id,))
        wallet = cur.fetchone()
        cur.close()
        conn.close()
        return wallet[0] if wallet else 0

    @staticmethod
    def GetCategoryIDsInDB():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT categorynumber, categoryname FROM categories")
        categories = cur.fetchall()
        cur.close()
        conn.close()
        return categories

    @staticmethod
    def Get_A_CategoryName(categorynumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT categoryname FROM categories WHERE categorynumber = %s", (categorynumber,))
        category_name = cur.fetchone()
        cur.close()
        conn.close()
        return category_name[0] if category_name else "None"

    @staticmethod
    def GetProductImageLink(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productimagelink FROM products WHERE productnumber = %s", (productnumber,))
        image_link = cur.fetchone()
        cur.close()
        conn.close()
        return image_link[0] if image_link else "None"

    @staticmethod
    def GetProductName(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productname FROM products WHERE productnumber = %s", (productnumber,))
        product_name = cur.fetchone()
        cur.close()
        conn.close()
        return product_name[0] if product_name else "None"

    @staticmethod
    def GetProductNumber(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productnumber FROM products WHERE productnumber = %s", (productnumber,))
        product_number = cur.fetchone()
        cur.close()
        conn.close()
        return product_number[0] if product_number else "None"

    @staticmethod
    def GetProductDescription(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productdescription FROM products WHERE productnumber = %s", (productnumber,))
        product_description = cur.fetchone()
        cur.close()
        conn.close()
        return product_description[0] if product_description else "None"

    @staticmethod
    def GetProductPrice(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productprice FROM products WHERE productnumber = %s", (productnumber,))
        product_price = cur.fetchone()
        cur.close()
        conn.close()
        return product_price[0] if product_price else "None"

    @staticmethod
    def GetProductQuantity(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productquantity FROM products WHERE productnumber = %s", (productnumber,))
        product_quantity = cur.fetchone()
        cur.close()
        conn.close()
        return product_quantity[0] if product_quantity else "None"

    @staticmethod
    def GetProductNumberName():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productnumber, productname FROM products")
        product_info = cur.fetchall()
        cur.close()
        conn.close()
        return product_info

    @staticmethod
    def GetProductIDs():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productnumber FROM products")
        product_ids = cur.fetchall()
        cur.close()
        conn.close()
        return product_ids

    @staticmethod
    def GetOrderDetails(ordernumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE ordernumber = %s", (ordernumber,))
        order_details = cur.fetchall()
        cur.close()
        conn.close()
        return order_details[0] if order_details else "None"

    @staticmethod
    def GetAllUnfirmedOrdersUser(buyerid):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ordernumber, productname, buyerusername, payment_id, productnumber FROM orders WHERE buyerid = %s and paidmethod = 'NO'", (buyerid,))
        orders = cur.fetchall()
        cur.close()
        conn.close()
        return orders

    @staticmethod
    def GetProductInfoByPName(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE productnumber = %s", (productnumber,))
        product_info = cur.fetchall()
        cur.close()
        conn.close()
        return product_info

    @staticmethod
    def GetProduct_A_AdminID(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT adminid FROM products WHERE productnumber = %s", (productnumber,))
        admin_id = cur.fetchone()
        cur.close()
        conn.close()
        return admin_id[0] if admin_id else "None"

    @staticmethod
    def GetOrderIDs_Buyer(buyerid):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ordernumber FROM orders WHERE buyerid = %s", (buyerid,))
        order_ids = cur.fetchall()
        cur.close()
        conn.close()
        return order_ids

    @staticmethod
    def GetAdminUsernamesInDB():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT usname FROM admins")
        admin_usernames = cur.fetchall()
        cur.close()
        conn.close()
        return admin_usernames

    @staticmethod
    def GetUsersInfo():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, usname, wallet FROM users")
        user_info = cur.fetchall()
        cur.close()
        conn.close()
        return user_info

    @staticmethod
    def GetOrderInfo():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ordernumber, productname, buyerusername FROM orders")
        order_info = cur.fetchall()
        cur.close()
        conn.close()
        return order_info

    @staticmethod
    def GetOrderIDs():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ordernumber FROM orders")
        order_ids = cur.fetchall()
        cur.close()
        conn.close()
        return order_ids

    @staticmethod
    def GetPaymentMethodsAll(methodname):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM paymentmethods WHERE methodname = %s", (methodname,))
        methods = cur.fetchall()
        cur.close()
        conn.close()
        return methods

    @staticmethod
    def GetPaymentMethodTokenKeysCleintID(methodname):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT token_clientid_keys FROM paymentmethods WHERE methodname = %s", (methodname,))
        token = cur.fetchone()
        cur.close()
        conn.close()
        return token[0] if token else "None"

    @staticmethod
    def GetProductInfos():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productnumber, productname, productprice FROM products")
        product_info = cur.fetchall()
        cur.close()
        conn.close()
        return product_info

    @staticmethod
    def GetProductDownloadLink(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productdownloadlink FROM products WHERE productnumber = %s", (productnumber,))
        download_link = cur.fetchone()
        cur.close()
        conn.close()
        return download_link[0] if download_link else "None"

class CleanData:
    @staticmethod
    def delete_a_product(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE productnumber = %s", (productnumber,))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def delete_a_category(categorynumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM categories WHERE categorynumber = %s", (categorynumber,))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def delete_an_order(ordernumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM orders WHERE ordernumber = %s", (ordernumber,))
        conn.commit()
        cur.close()
        conn.close()

# Localization
LANGUAGES = {
    'en': 'English',
    'ru': 'Русский',
    'tj': 'Тоҷикӣ',
}

# ... (rest of localization texts)

def get_user_language(chat_id):
    """Gets the user's language from the database."""
    conn = get_db_connection()
    lang = 'en' # Default to English
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT language FROM users WHERE id = %s", (chat_id,))
            result = cur.fetchone()
            if result and result[0] in LANGUAGES:
                lang = result[0]
        except psycopg2.Error as e:
            print(f"Database error in get_user_language: {e}")
        finally:
            cur.close()
            conn.close()
    return lang

def get_text(chat_id, key):
    """Gets the translated text for a given key and user."""
    lang = get_user_language(chat_id)
    return TEXTS.get(key, {}).get(lang, f"<{key}>")

# Utils
def create_main_keyboard(chat_id):
    """Create the main user keyboard"""
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.row_width = 2
    key1 = types.KeyboardButton(text=get_text(chat_id, 'shop_items'))
    key2 = types.KeyboardButton(text=get_text(chat_id, 'my_orders'))
    key3 = types.KeyboardButton(text=get_text(chat_id, 'support'))
    keyboard.add(key1)
    keyboard.add(key2, key3)
    return keyboard

# Purchase
class UserOperations:
    def shop_items(message):
        id = message.from_user.id
        usname = message.chat.username
        products_list = GetDataFromDB.GetProductInfo()
        id = message.from_user.id
        all_categories = GetDataFromDB.GetCategoryIDsInDB()
        keyboard = types.InlineKeyboardMarkup()
        if all_categories == []:
            bot.send_message(id, get_text(id, 'no_product_available_soon'))
        else:
            for catnum, catname in all_categories:
                c_catname = catname.upper()
                products_category = GetDataFromDB.GetCategoryNumProduct(c_catname)
                for ctg in products_category:
                    products_in_category = ctg[0]
                    text_but = f"🏷 {catname} ({products_in_category})"
                    text_cal = f"getcats_{catnum}"
                    keyboard.add(types.InlineKeyboardButton(text=text_but, callback_data=text_cal))
        

            bot.send_message(id, get_text(id, 'categories_list'), reply_markup=keyboard)
            bot.send_message(id, get_text(id, 'list_completed'), reply_markup=types.ReplyKeyboardRemove())
            for productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory in products_list:
                list_m =  [productnumber, productname, productprice]

    def purchase_a_products(message, input_cate):
        id = message.from_user.id
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        def checkint():
            try:
                input_cat = int(input_cate)
                return input_cat
            except:
                return input_cate

        input_product_id = checkint()
        if isinstance(input_product_id, int) == True:
            product_list = GetDataFromDB.GetProductInfoByPName(input_product_id)
            if f"{input_product_id}" in f"{product_list}":
                keyboard2 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                key1 = types.KeyboardButton(text="Bitcoin ฿")
                keyboard2.add(key1)
                for productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory in product_list:
                    list_m =  [productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory]
                    bot.send_message(id, get_text(id, 'select_payment_method'), reply_markup=keyboard2)
                global order_info
                order_info = list_m
            else:
                print(get_text(id, 'wrong_command'))
    def orderdata():
        try:
            1==1
            print(order_info)
            return  order_info
        except:
            return None

# Categories
class CategoriesDatas:
    def get_category_products(message, input_cate):
        id = message.from_user.id
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.row_width = 2
        buyer_id = message.from_user.id
        buyer_username = message.from_user.username
        all_categories = GetDataFromDB.GetCategoryIDsInDB()
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
            if f"{product_cate}" in f"{categories}":
                product_category = product_cate.upper()
                product_list = GetDataFromDB.GetProductInfoByCTGName(product_category)
                print(product_list)
                if product_list == []:
                    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                    keyboard.row_width = 2
                    key1 = types.KeyboardButton(text=get_text(id, 'shop_items'))
                    key2 = types.KeyboardButton(text=get_text(id, 'my_orders'))
                    key3 = types.KeyboardButton(text=get_text(id, 'support'))
                    keyboard.add(key1)
                    keyboard.add(key2, key3)
                    bot.send_message(id, get_text(id, 'no_product_in_store'), reply_markup=create_main_keyboard(id))
                else:
                    bot.send_message(id, get_text(id, 'category_products').format(product_cate=product_cate))
                    for productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory in product_list:
                        keyboard2 = types.InlineKeyboardMarkup()
                        keyboard2.add(types.InlineKeyboardButton(text=get_text(id, 'buy_now'), callback_data=f"getproduct_{productnumber}"))
                        bot.send_photo(id, photo=f"{productimagelink}", caption=get_text(id, 'product_details_short').format(productnumber=productnumber, productname=productname, productprice=productprice, StoreCurrency=store_currency, productquantity=productquantity, productdescription=productdescription), reply_markup=keyboard2)

            else:
                print(get_text(id, 'wrong_command'))

# Flask App
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

@flask_app.route('/', methods=['GET', 'POST'])
def webhook():
    """Handle incoming webhook requests from Telegram."""
    if flask.request.method == 'GET':
        return 'Bot is running!', 200
    
    if flask.request.headers.get('content-type') == 'application/json':
        try:
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return '', 200
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            return 'Error processing update', 500
    else:
        logger.warning(f"Invalid webhook request received. Content-Type: {flask.request.headers.get('content-type')}")
        return 'Invalid request', 403

# Main bot handlers
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Handle callback queries from inline keyboards"""
    try:
        if call.data.startswith("set_lang_"):
            lang_code = call.data.split('_')[2]
            CreateDatas.update_user_language(call.message.chat.id, lang_code)
            bot.send_message(call.message.chat.id, get_text(call.message.chat.id, 'language_updated'))
            send_welcome(call.message)
        elif call.data.startswith("getcats_"):
            input_catees = call.data.replace('getcats_','')
            CategoriesDatas.get_category_products(call, input_catees)
        elif call.data.startswith("getproduct_"):
            input_cate = call.data.replace('getproduct_','')
            UserOperations.purchase_a_products(call, input_cate)
        elif call.data.startswith("managecats_"):
            input_cate = call.data.replace('managecats_','')
            manage_categoriesbutton(call, input_cate)
        else:
            logger.warning(f"Unknown callback data: {call.data}")
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        bot.send_message(call.message.chat.id, "An error occurred. Please try again.")

# ... (rest of the bot handlers)

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        flask_app.run(debug=False, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Error starting Flask application: {e}")
        exit(1)
