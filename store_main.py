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
                        wallet INTEGER DEFAULT 0
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
    """Database data creation and insertion operations"""

    @staticmethod
    def AddAuser(user_id, username):
        """Add a new user to the database or do nothing if user exists."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (id, usname, wallet) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING", (user_id, username, 0))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def AddAdmin(admin_id, username):
        """Add a new admin to the database or do nothing if admin exists."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO admins (id, usname) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING", (admin_id, username))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def AddProduct(productnumber, admin_id, username):
        """Add a new product with default values."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO products
            (productnumber, adminid, adminusname, productname, productdescription, productprice, productimagelink, productdownloadlink, productkeysfile, productquantity, productcategory)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (productnumber, admin_id, username, 'NIL', 'NIL', 0, 'NIL', 'https://nil.nil', 'NIL', 0, 'Default Category'))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def AddOrder(buyer_id, username, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, ordernumber, productnumber, payment_id):
        """Add a new order to the database."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO orders
            (buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, buyercomment, ordernumber, productnumber, payment_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (buyer_id, username, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, 'NIL', ordernumber, productnumber, payment_id))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def AddCategory(categorynumber, categoryname):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO categories (categorynumber, categoryname) VALUES (%s, %s) ON CONFLICT (categorynumber) DO NOTHING", (categorynumber, categoryname))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def AddPaymentMethod(id, username, method_name):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO paymentmethods (adminid, adminusname, methodname) VALUES (%s, %s, %s) ON CONFLICT (methodname) DO NOTHING", (id, username, method_name))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateOrderConfirmed(paidmethod, ordernumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE orders SET paidmethod = %s WHERE ordernumber = %s", (paidmethod, ordernumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdatePaymentMethodToken(id, username, token_keys_clientid, method_name):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE paymentmethods SET adminid = %s, adminusname = %s, token_clientid_keys = %s WHERE method_name = %s", (id, username, token_keys_clientid, method_name))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdatePaymentMethodSecret(id, username, secret_keys, method_name):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE paymentmethods SET adminid = %s, adminusname = %s, sectret_keys = %s WHERE method_name = %s", (id, username, secret_keys, method_name))
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
    def UpdateOrderComment(buyercomment, ordernumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE orders SET buyercomment = %s WHERE ordernumber = %s", (buyercomment, ordernumber))
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
    def UpdateProductName(productname, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productname = %s WHERE productnumber = %s", (productname, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductDescription(productdescription, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productdescription = %s WHERE productnumber = %s", (productdescription, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductPrice(productprice, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productprice = %s WHERE productnumber = %s", (productprice, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductproductimagelink(productimagelink, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productimagelink = %s WHERE productnumber = %s", (productimagelink, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductproductdownloadlink(productdownloadlink, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productdownloadlink = %s WHERE productnumber = %s", (productdownloadlink, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductKeysFile(productkeysfile, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productkeysfile = %s WHERE productnumber = %s", (productkeysfile, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductQuantity(productquantity, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productquantity = %s WHERE productnumber = %s", (productquantity, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def UpdateProductCategory(productcategory, productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productcategory = %s WHERE productnumber = %s", (productcategory, productnumber))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def Update_All_ProductCategory(new_category, productcategory):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET productcategory = %s WHERE productcategory = %s", (new_category, productcategory))
        conn.commit()
        cur.close()
        conn.close()

class GetDataFromDB:
    """Database query operations"""

    @staticmethod
    def GetUserWalletInDB(userid):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT wallet FROM users WHERE id = %s", (userid,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else 0

    @staticmethod
    def GetUserNameInDB(userid):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT usname FROM users WHERE id = %s", (userid,))
        shopuser = cur.fetchone()
        cur.close()
        conn.close()
        return shopuser[0] if shopuser else ""

    @staticmethod
    def GetAdminNameInDB(userid):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT usname FROM admins WHERE id = %s", (userid,))
        shopuser = cur.fetchone()
        cur.close()
        conn.close()
        return shopuser[0] if shopuser else ""

    @staticmethod
    def GetUserIDsInDB():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users")
        shopuser = cur.fetchall()
        cur.close()
        conn.close()
        return shopuser

    @staticmethod
    def GetProductName(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productname FROM products WHERE productnumber = %s", (productnumber,))
        productname = cur.fetchone()
        cur.close()
        conn.close()
        return productname[0] if productname else None

    @staticmethod
    def GetProductDescription(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productdescription FROM products WHERE productnumber = %s", (productnumber,))
        productdescription = cur.fetchone()
        cur.close()
        conn.close()
        return productdescription[0] if productdescription else None

    @staticmethod
    def GetProductPrice(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productprice FROM products WHERE productnumber = %s", (productnumber,))
        productprice = cur.fetchone()
        cur.close()
        conn.close()
        return productprice[0] if productprice else None

    @staticmethod
    def GetProductImageLink(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productimagelink FROM products WHERE productnumber = %s", (productnumber,))
        productimagelink = cur.fetchone()
        cur.close()
        conn.close()
        return productimagelink[0] if productimagelink else None

    @staticmethod
    def GetProductDownloadLink(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productdownloadlink FROM products WHERE productnumber = %s", (productnumber,))
        productdownloadlink = cur.fetchone()
        cur.close()
        conn.close()
        return productdownloadlink[0] if productdownloadlink else None

    @staticmethod
    def GetProductNumber(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productnumber FROM products WHERE productnumber = %s", (productnumber,))
        productnumbers = cur.fetchone()
        cur.close()
        conn.close()
        return productnumbers[0] if productnumbers else None

    @staticmethod
    def GetProductQuantity(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productquantity FROM products WHERE productnumber = %s", (productnumber,))
        productquantity = cur.fetchone()
        cur.close()
        conn.close()
        return productquantity[0] if productquantity else None

    @staticmethod
    def GetProduct_A_Category(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productcategory FROM products WHERE productnumber = %s", (productnumber,))
        productcategory = cur.fetchone()
        cur.close()
        conn.close()
        return productcategory[0] if productcategory else None

    @staticmethod
    def Get_A_CategoryName(categorynumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT categoryname FROM categories WHERE categorynumber = %s", (categorynumber,))
        productcategory = cur.fetchone()
        cur.close()
        conn.close()
        return productcategory[0] if productcategory else None

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
    def GetCategoryNumProduct(productcategory):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM products WHERE productcategory = %s", (productcategory,))
        categories = cur.fetchall()
        cur.close()
        conn.close()
        return categories

    @staticmethod
    def GetProduct_A_AdminID(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT adminid FROM products WHERE productnumber = %s", (productnumber,))
        admin_id = cur.fetchone()
        cur.close()
        conn.close()
        return admin_id[0] if admin_id else None

    @staticmethod
    def GetAdminIDsInDB():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM admins")
        shopadmin = cur.fetchall()
        cur.close()
        conn.close()
        return shopadmin

    @staticmethod
    def GetAdminUsernamesInDB():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT usname FROM admins")
        shopadmin = cur.fetchall()
        cur.close()
        conn.close()
        return shopadmin

    @staticmethod
    def GetProductNumberName():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productnumber, productname FROM products")
        productnumbers_name = cur.fetchall()
        cur.close()
        conn.close()
        return productnumbers_name

    @staticmethod
    def GetProductInfos():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productnumber, productname, productprice FROM products")
        productnumbers_name = cur.fetchall()
        cur.close()
        conn.close()
        return productnumbers_name

    @staticmethod
    def GetProductInfo():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory FROM products")
        productnumbers_name = cur.fetchall()
        cur.close()
        conn.close()
        return productnumbers_name

    @staticmethod
    def GetProductInfoByCTGName(productcategory):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory FROM products WHERE productcategory = %s", (productcategory,))
        productnumbers_name = cur.fetchall()
        cur.close()
        conn.close()
        return productnumbers_name

    @staticmethod
    def GetProductInfoByPName(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory FROM products WHERE productnumber = %s", (productnumber,))
        productnumbers_name = cur.fetchall()
        cur.close()
        conn.close()
        return productnumbers_name

    @staticmethod
    def GetUsersInfo():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, usname, wallet FROM users")
        user_infos = cur.fetchall()
        cur.close()
        conn.close()
        return user_infos

    @staticmethod
    def AllUsers():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(id) FROM users")
        alluser = cur.fetchall()
        cur.close()
        conn.close()
        return alluser if alluser else 0

    @staticmethod
    def AllAdmins():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(id) FROM admins")
        alladmin = cur.fetchall()
        cur.close()
        conn.close()
        return alladmin if alladmin else 0

    @staticmethod
    def AllProducts():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(productnumber) FROM products")
        allproduct = cur.fetchall()
        cur.close()
        conn.close()
        return allproduct if allproduct else 0

    @staticmethod
    def AllOrders():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(ordernumber) FROM orders")
        allorder = cur.fetchall()
        cur.close()
        conn.close()
        return allorder if allorder else 0

    @staticmethod
    def GetAdminsInfo():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, usname, wallet FROM admins")
        admin_infos = cur.fetchall()
        cur.close()
        conn.close()
        return admin_infos

    @staticmethod
    def GetOrderInfo():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ordernumber, productname, buyerusername FROM orders")
        order_infos = cur.fetchall()
        cur.close()
        conn.close()
        return order_infos

    @staticmethod
    def GetPaymentMethods():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT method_name, adminusname FROM paymentmethods") # 'activated' column doesn't exist
        payment_method = cur.fetchall()
        cur.close()
        conn.close()
        return payment_method

    @staticmethod
    def GetPaymentMethodsAll(method_name):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT methodname, token_clientid_keys, sectret_keys FROM paymentmethods WHERE methodname = %s", (method_name,))
        payment_method = cur.fetchall()
        cur.close()
        conn.close()
        return payment_method

    @staticmethod
    def GetPaymentMethodTokenKeysCleintID(method_name):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT token_clientid_keys FROM paymentmethods WHERE methodname = %s", (method_name,))
        payment_method = cur.fetchone()
        cur.close()
        conn.close()
        return payment_method[0] if payment_method else None

    @staticmethod
    def GetPaymentMethodSecretKeys(method_name):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT sectret_keys FROM paymentmethods WHERE methodname = %s", (method_name,))
        payment_method = cur.fetchone()
        cur.close()
        conn.close()
        return payment_method[0] if payment_method else None

    @staticmethod
    def GetAllPaymentMethodsInDB():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT methodname FROM paymentmethods")
        payment_methods = cur.fetchall()
        cur.close()
        conn.close()
        return payment_methods

    @staticmethod
    def GetProductCategories():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT productcategory FROM products")
        productcategory = cur.fetchall()
        cur.close()
        conn.close()
        return productcategory

    @staticmethod
    def GetProductIDs():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT productnumber FROM products")
        productnumbers = cur.fetchall()
        cur.close()
        conn.close()
        return productnumbers

    @staticmethod
    def GetOrderDetails(ordernumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, buyercomment, ordernumber, productnumber FROM orders WHERE ordernumber = %s AND paidmethod != 'NO'", (ordernumber,))
        order_details = cur.fetchall()
        cur.close()
        conn.close()
        return order_details

    @staticmethod
    def GetOrderIDs_Buyer(buyerid):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ordernumber FROM orders WHERE buyerid = %s AND paidmethod != 'NO'", (buyerid,))
        productnumbers = cur.fetchall()
        cur.close()
        conn.close()
        return productnumbers

    @staticmethod
    def GetOrderIDs():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ordernumber FROM orders")
        productnumbers = cur.fetchall()
        cur.close()
        conn.close()
        return productnumbers

    @staticmethod
    def GetAllUnfirmedOrdersUser(buyerid):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ordernumber, productname, buyerusername, payment_id, productnumber FROM orders WHERE paidmethod = 'NO' AND buyerid = %s AND payment_id != ordernumber", (buyerid,))
        payment_method = cur.fetchall()
        cur.close()
        conn.close()
        return payment_method

class CleanData:
    """Database data deletion operations"""

    @staticmethod
    def CleanShopUserTable():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users")
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def CleanShopProductTable():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM products")
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def delete_a_product(productnumber):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE productnumber = %s", (productnumber,))
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

    @staticmethod
    def delete_a_payment_method(method_name):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM paymentmethods WHERE methodname = %s", (method_name,))
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

# Set webhook
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")
if WEBHOOK_URL:
    logger.info(f"Found RENDER_EXTERNAL_URL: {WEBHOOK_URL}")
    bot.remove_webhook()
    time.sleep(0.5)
    bot.set_webhook(url=WEBHOOK_URL)
    logger.info("Webhook set successfully to the Render external URL.")
else:
    logger.info("RENDER_EXTERNAL_URL not set. Assuming local development (polling).")


# Utils
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
            bot.send_message(id, "⚠️ No Product available at the moment, kindly check back soon")
        else:
            for catnum, catname in all_categories:
                c_catname = catname.upper()
                products_category = GetDataFromDB.GetCategoryNumProduct(c_catname)
                for ctg in products_category:
                    products_in_category = ctg[0]
                    text_but = f"🏷 {catname} ({products_in_category})"
                    text_cal = f"getcats_{catnum}"
                    keyboard.add(types.InlineKeyboardButton(text=text_but, callback_data=text_cal))
        
            bot.send_message(id, "CATEGORIES:", reply_markup=keyboard)
            bot.send_message(id, "List completed ✅", reply_markup=types.ReplyKeyboardRemove())
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
                    bot.send_message(id, "💡 Select a Payment method to pay for this product 👇", reply_markup=keyboard2)
            else:
                print("Wrong command !!!")

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
                    bot.send_message(id, "No Product in the store", reply_markup=create_main_keyboard())
                else:
                    bot.send_message(id, f"{product_cate} Category's Products")
                    for productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory in product_list:
                        keyboard2 = types.InlineKeyboardMarkup()
                        keyboard2.add(types.InlineKeyboardButton(text="BUY NOW 💰", callback_data=f"getproduct_{productnumber}"))
                        bot.send_photo(id, photo=f"{productimagelink}", caption=f"Product ID 🪪: /{productnumber}\n\nProduct Name 📦: {productname}\n\nProduct Price 💰: {productprice} {store_currency}\n\nProducts In Stock 🛍: {productquantity}\n\nProduct Description 💬: {productdescription}", reply_markup=keyboard2)

            else:
                print("Wrong command !!!")

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
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Send a welcome message and the main keyboard."""
    CreateDatas.AddAuser(message.from_user.id, message.chat.username)
    bot.reply_to(message, "Welcome to the Store Bot!", reply_markup=create_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Handle callback queries from inline keyboards"""
    try:
        if call.data.startswith("getcats_"):
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

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        flask_app.run(debug=False, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Error starting Flask application: {e}")
        exit(1)
