import os
import psycopg2
from dotenv import load_dotenv
import logging

# Load environment variables first
load_dotenv('config.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
logger.info(f"DATABASE_URL: {DATABASE_URL}")


if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set. Please set it in your Render environment.")

def get_db_connection():
    """Establish and return a database connection"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

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
    def GetUserIDsInDB():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users")
        user_ids = cur.fetchall()
        cur.close()
        conn.close()
        return user_ids

    @staticmethod
    def GetUserLanguage(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT language FROM users WHERE id = %s", (user_id,))
        language = cur.fetchone()
        cur.close()
        conn.close()
        if language:
            return language[0]
        return 'en' # Default to English

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
