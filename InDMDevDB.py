import os
import psycopg2
from datetime import datetime
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
db_connection = psycopg2.connect(DATABASE_URL)
cursor = db_connection.cursor()
db_lock = threading.Lock()

class CreateTables:
    """Database table creation and management"""
    
    @staticmethod
    def create_all_tables():
        """Create all necessary database tables"""
        try:
            with db_lock:
                # Create ShopUserTable
                cursor.execute("""CREATE TABLE IF NOT EXISTS ShopUserTable(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    wallet INTEGER DEFAULT 0,
                    language TEXT DEFAULT 'en',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")
                
                # Create ShopAdminTable
                cursor.execute("""CREATE TABLE IF NOT EXISTS ShopAdminTable(
                    id SERIAL PRIMARY KEY,
                    admin_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    wallet INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")

                # Create ShopProductTable
                cursor.execute("""CREATE TABLE IF NOT EXISTS ShopProductTable(
                    id SERIAL PRIMARY KEY,
                    productnumber INTEGER UNIQUE NOT NULL,
                    admin_id INTEGER NOT NULL,
                    username TEXT,
                    productname TEXT NOT NULL,
                    productdescription TEXT,
                    productprice INTEGER DEFAULT 0,
                    productimagelink TEXT,
                    productdownloadlink TEXT,
                    productkeysfile TEXT,
                    productquantity INTEGER DEFAULT 0,
                    productcategory TEXT DEFAULT 'Default Category',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")

                # Create ShopOrderTable
                cursor.execute("""CREATE TABLE IF NOT EXISTS ShopOrderTable(
                    id SERIAL PRIMARY KEY,
                    buyerid INTEGER NOT NULL,
                    buyerusername TEXT,
                    productname TEXT NOT NULL,
                    productprice TEXT NOT NULL,
                    orderdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paidmethod TEXT DEFAULT 'NO',
                    productdownloadlink TEXT,
                    productkeys TEXT,
                    buyercomment TEXT,
                    ordernumber INTEGER UNIQUE NOT NULL,
                    productnumber INTEGER NOT NULL,
                    payment_id TEXT
                )""")
                
                # Create ShopCategoryTable
                cursor.execute("""CREATE TABLE IF NOT EXISTS ShopCategoryTable(
                    id SERIAL PRIMARY KEY,
                    categorynumber INTEGER UNIQUE NOT NULL,
                    categoryname TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")
                
                # Create PaymentMethodTable
                cursor.execute("""CREATE TABLE IF NOT EXISTS PaymentMethodTable(
                    id SERIAL PRIMARY KEY,
                    admin_id INTEGER,
                    username TEXT,
                    method_name TEXT UNIQUE NOT NULL,
                    token_keys_clientid TEXT,
                    secret_keys TEXT,
                    activated TEXT DEFAULT 'NO',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")
                
                db_connection.commit()
                logger.info("All database tables created successfully")
                
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            db_connection.rollback()
            raise
        
# Initialize tables
CreateTables.create_all_tables()

class CreateDatas:
    """Database data creation and insertion operations"""
    
    @staticmethod
    def add_user(user_id, username):
        """Add a new user to the database"""
        try:
            with db_lock:
                cursor.execute(
                    "INSERT INTO ShopUserTable (user_id, username, wallet) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO NOTHING",
                    (user_id, username, 0)
                )
                db_connection.commit()
                logger.info(f"User added: {username} (ID: {user_id})")
                return True
        except Exception as e:
            logger.error(f"Error adding user {username}: {e}")
            db_connection.rollback()
            return False
            
    @staticmethod
    def add_admin(admin_id, username):
        """Add a new admin to the database"""
        try:
            with db_lock:
                cursor.execute(
                    "INSERT INTO ShopAdminTable (admin_id, username, wallet) VALUES (%s, %s, %s) ON CONFLICT (admin_id) DO NOTHING",
                    (admin_id, username, 0)
                )
                db_connection.commit()
                logger.info(f"Admin added: {username} (ID: {admin_id})")
                return True
        except Exception as e:
            logger.error(f"Error adding admin {username}: {e}")
            db_connection.rollback()
            return False

    @staticmethod
    def add_product(productnumber, admin_id, username):
        """Add a new product to the database"""
        try:
            with db_lock:
                cursor.execute("""
                    INSERT INTO ShopProductTable 
                    (productnumber, admin_id, username, productname, productdescription, 
                     productprice, productimagelink, productdownloadlink, productkeysfile, 
                     productquantity, productcategory) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (productnumber, admin_id, username, 'NIL', 'NIL', 0, 'NIL', 
                      'https://nil.nil', 'NIL', 0, 'Default Category'))
                db_connection.commit()
                logger.info(f"Product {productnumber} added by admin {username}")
                return True
        except Exception as e:
            logger.error(f"Error adding product {productnumber}: {e}")
            db_connection.rollback()
            return False
    
    # Backward compatibility methods
    @staticmethod
    def AddAuser(user_id, username):
        """Backward compatibility wrapper for add_user"""
        return CreateDatas.add_user(user_id, username)
    
    @staticmethod
    def AddAdmin(admin_id, username):
        """Backward compatibility wrapper for add_admin"""
        return CreateDatas.add_admin(admin_id, username)
    
    @staticmethod
    def AddProduct(productnumber, admin_id, username):
        """Backward compatibility wrapper for add_product"""
        return CreateDatas.add_product(productnumber, admin_id, username)

    @staticmethod
    def AddOrder(buyer_id, username, productname, productprice, orderdate, paidmethod, 
                 productdownloadlink, productkeys, ordernumber, productnumber, payment_id):
        """Add a new order to the database"""
        try:
            with db_lock:
                cursor.execute(
                    "INSERT INTO ShopOrderTable (buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, buyercomment, ordernumber, productnumber, payment_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (buyer_id, username, productname, productprice, orderdate,
                      paidmethod, productdownloadlink, productkeys, 'NIL', 
                      ordernumber, productnumber, payment_id)
                )
                db_connection.commit()
                logger.info(f"Order {ordernumber} added for user {username}")
                return True
        except Exception as e:
            logger.error(f"Error adding order {ordernumber}: {e}")
            db_connection.rollback()
            return False

    def AddCategory(categorynumber, categoryname):
        try:
            with db_lock:
                cursor.execute(
                    "INSERT INTO ShopCategoryTable (categorynumber, categoryname) VALUES (%s, %s)",
                    (categorynumber, categoryname)
                )
                db_connection.commit()
        except Exception as e:
            print(e)

    def AddEmptyRow():
        with db_lock:
            cursor.execute("INSERT INTO PaymentMethodTable (admin_id, username, method_name, activated) VALUES ('None', 'None', 'None', 'None')")
            db_connection.commit()
    
    def AddCryptoPaymentMethod(id, username, token_keys_clientid, secret_keys, method_name):
        try:
            with db_lock:
                cursor.execute("UPDATE PaymentMethodTable SET admin_id = %s, username = %s, token_keys_clientid = %s, secret_keys = %s, activated = 'NO' WHERE method_name = %s", (id, username, token_keys_clientid, secret_keys, method_name))
                db_connection.commit()
        except Exception as e:
            print(e)

    def UpdateOrderConfirmed(paidmethod, ordernumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopOrderTable SET paidmethod = %s WHERE ordernumber = %s", (paidmethod, ordernumber))
                db_connection.commit()
        except Exception as e:
            print(e)

    def UpdatePaymentMethodToken(id, username, token_keys_clientid, method_name):
        try:
            with db_lock:
                cursor.execute("UPDATE PaymentMethodTable SET admin_id = %s, username = %s, token_keys_clientid = %s WHERE method_name = %s", (id, username, token_keys_clientid, method_name))
                db_connection.commit()
        except Exception as e:
            print(e)

    def UpdatePaymentMethodSecret(id, username, secret_keys, method_name):
        try:
            with db_lock:
                cursor.execute("UPDATE PaymentMethodTable SET admin_id = %s, username = %s, secret_keys = %s WHERE method_name = %s", (id, username, secret_keys, method_name))
                db_connection.commit()
        except Exception as e:
            print(e)

    def Update_A_Category(categoryname, categorynumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopCategoryTable SET categoryname = %s WHERE categorynumber = %s", (categoryname, categorynumber))
                db_connection.commit()
        except Exception as e:
            print(e)

    def UpdateOrderComment(buyercomment, ordernumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopOrderTable SET buyercomment = %s WHERE ordernumber = %s", (buyercomment, ordernumber))
                db_connection.commit()
        except Exception as e:
            print(e)

    def UpdateOrderPaymentMethod(paidmethod, ordernumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopOrderTable SET paidmethod = %s WHERE ordernumber = %s", (paidmethod, ordernumber))
                db_connection.commit()
        except Exception as e:
            print(e)

    def UpdateOrderPurchasedKeys(productkeys, ordernumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopOrderTable SET productkeys = %s WHERE ordernumber = %s", (productkeys, ordernumber))
                db_connection.commit()
        except Exception as e:
            print(e)


    def AddPaymentMethod(id, username, method_name):
        with db_lock:
            cursor.execute("INSERT INTO PaymentMethodTable (admin_id, username, method_name, activated) VALUES (%s, %s, %s, 'YES')", (id, username, method_name))
            db_connection.commit()

    def UpdateProductName(productname, productnumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopProductTable SET productname = %s WHERE productnumber = %s", (productname, productnumber))
                db_connection.commit()
        except Exception as e:
            print(e)

    def UpdateProductDescription(productdescription, productnumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopProductTable SET productdescription = %s WHERE productnumber = %s", (productdescription, productnumber))
                db_connection.commit()
        except Exception as e:
            print(e)
    
    def UpdateProductPrice(productprice, productnumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopProductTable SET productprice = %s WHERE productnumber = %s", (productprice, productnumber))
                db_connection.commit()
        except Exception as e:
            print(e)
    
    def UpdateProductproductimagelink(productimagelink, productnumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopProductTable SET productimagelink = %s WHERE productnumber = %s", (productimagelink, productnumber))
                db_connection.commit()
        except Exception as e:
            print(e)

    def UpdateProductproductdownloadlink(productdownloadlink, productnumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopProductTable SET productdownloadlink = %s WHERE productnumber = %s", (productdownloadlink, productnumber))
                db_connection.commit()
        except Exception as e:
            print(e)
    
    def UpdateProductKeysFile(productkeysfile, productnumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopProductTable SET productkeysfile = %s WHERE productnumber = %s", (productkeysfile, productnumber))
                db_connection.commit()
        except Exception as e:
            print(e)
    
    def UpdateProductQuantity(productquantity, productnumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopProductTable SET productquantity = %s WHERE productnumber = %s", (productquantity, productnumber))
                db_connection.commit()
        except Exception as e:
            print(e)
    
    def UpdateProductCategory(productcategory, productnumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopProductTable SET productcategory = %s WHERE productnumber = %s", (productcategory, productnumber))
                db_connection.commit()
        except Exception as e:
            print(e)

    def UpdateProductQuantity(productquantity, productnumber):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopProductTable SET productquantity = %s WHERE productnumber = %s", (productquantity, productnumber))
                db_connection.commit()
        except Exception as e:
            print(e)

    def Update_All_ProductCategory(new_category, productcategory):
        try:
            with db_lock:
                cursor.execute("UPDATE ShopProductTable SET productcategory = %s WHERE productcategory = %s", (new_category, productcategory))
                db_connection.commit()
        except Exception as e:
            print(e)

    def update_user_language(user_id, language):
        """Update the user's language."""
        try:
            with db_lock:
                cursor.execute(
                    "UPDATE ShopUserTable SET language = %s WHERE user_id = %s",
                    (language, user_id)
                )
                db_connection.commit()
                logger.info(f"Language for user {user_id} updated to {language}")
                return True
        except Exception as e:
            logger.error(f"Error updating language for user {user_id}: {e}")
            db_connection.rollback()
            return False

class GetDataFromDB:
    """Database query operations"""
    
    @staticmethod
    def GetUserWalletInDB(userid):
        """Get user wallet balance from database"""
        try:
            with db_lock:
                cursor.execute("SELECT wallet FROM ShopUserTable WHERE user_id = %s", (userid,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting user wallet for {userid}: {e}")
            return 0

    def get_user_language(user_id):
        """Get the user's language from the database."""
        try:
            with db_lock:
                cursor.execute("SELECT language FROM ShopUserTable WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                return result[0] if result else 'en'
        except Exception as e:
            logger.error(f"Error getting language for user {user_id}: {e}")
            return 'en'
        
    def GetUserNameInDB(userid):
        try:
            with db_lock:
                cursor.execute("SELECT username FROM ShopUserTable WHERE user_id = %s", (userid,))
                shopuser = cursor.fetchone()[0]
                return shopuser
        except Exception as e:
            print(e)
            return ""
        
    def GetAdminNameInDB(userid):
        try:
            with db_lock:
                cursor.execute("SELECT username FROM ShopAdminTable WHERE admin_id = %s", (userid,))
                shopuser = cursor.fetchone()[0]
                return shopuser
        except Exception as e:
            print(e)
            return ""
        
    def GetUserIDsInDB():
        try:
            with db_lock:
                cursor.execute("SELECT user_id FROM ShopUserTable")
                shopuser = cursor.fetchall()
                return shopuser
        except Exception as e:
            print(e)
            return None

    def GetProductName(productnumber):
        try:
            with db_lock:
                cursor.execute("SELECT productname FROM ShopProductTable WHERE productnumber = %s", (productnumber,))
                productname = cursor.fetchone()[0]
                return productname
        except Exception as e:
            print(e)
            return None

    def GetProductDescription(productnumber):
        try:
            with db_lock:
                cursor.execute("SELECT productdescription FROM ShopProductTable WHERE productnumber = %s", (productnumber,))
                productdescription = cursor.fetchone()[0]
                return productdescription
        except Exception as e:
            print(e)
            return None

    def GetProductPrice(productnumber):
        try:
            with db_lock:
                cursor.execute("SELECT productprice FROM ShopProductTable WHERE productnumber = %s", (productnumber,))
                productprice = cursor.fetchone()[0]
                return productprice
        except Exception as e:
            print(e)
            return None
        
    def GetProductImageLink(productnumber):
        try:
            with db_lock:
                cursor.execute("SELECT productimagelink FROM ShopProductTable WHERE productnumber = %s", (productnumber,))
                productimagelink = cursor.fetchone()[0]
                return productimagelink
        except Exception as e:
            print(e)
            return None
    
    def GetProductDownloadLink(productnumber):
        try:
            with db_lock:
                cursor.execute("SELECT productdownloadlink FROM ShopProductTable WHERE productnumber = %s", (productnumber,))
                productimagelink = cursor.fetchone()[0]
                return productimagelink
        except Exception as e:
            print(e)
            return None

    def GetProductNumber(productnumber):
        try:
            with db_lock:
                cursor.execute("SELECT productnumber FROM ShopProductTable WHERE productnumber = %s", (productnumber,))
                productnumbers = cursor.fetchone()[0]
                return productnumbers
        except Exception as e:
            print(e)
            return None

    def GetProductQuantity(productnumber):
        try:
            with db_lock:
                cursor.execute("SELECT productquantity FROM ShopProductTable WHERE productnumber = %s", (productnumber,))
                productprice = cursor.fetchone()[0]
                return productprice
        except Exception as e:
            print(e)
            return None

    def GetProduct_A_Category(productnumber):
        try:
            with db_lock:
                cursor.execute("SELECT productcategory FROM ShopProductTable WHERE productnumber = %s", (productnumber,))
                productcategory = cursor.fetchone()[0]
                return productcategory
        except Exception as e:
            print(e)
            return None

    def Get_A_CategoryName(categorynumber):
        try: 
            with db_lock:
                cursor.execute("SELECT DISTINCT categoryname FROM ShopCategoryTable WHERE categorynumber = %s", (categorynumber,))
                productcategory = cursor.fetchone()[0]
                if productcategory is not None:
                    return productcategory
                else:
                    return None
        except Exception as e:
            print(e)
            return None

    def GetCategoryIDsInDB():
        try:
            with db_lock:
                cursor.execute("SELECT categorynumber, categoryname FROM ShopCategoryTable")
                categories =  cursor.fetchall()
                if categories is not None:
                    return categories
                else:
                    return None
        except Exception as e:
            print(e)
            return None

    def GetCategoryNumProduct(productcategory):
        try:
            with db_lock:
                cursor.execute("SELECT COUNT(*) FROM ShopProductTable WHERE productcategory = %s", (productcategory,))
                categories =  cursor.fetchall()
                if categories is not None:
                    return categories
                else:
                    return None
        except Exception as e:
            print(e)
            return None
        
    def GetProduct_A_AdminID(productnumber):
        try:
            with db_lock:
                cursor.execute("SELECT admin_id FROM ShopProductTable WHERE productnumber = %s", (productnumber,))
                productcategory = cursor.fetchone()[0]
                return productcategory
        except Exception as e:
            print(e)
            return None

    def GetAdminIDsInDB():
        try:
            with db_lock:
                cursor.execute("SELECT admin_id FROM ShopAdminTable")
                shopadmin =  cursor.fetchall()
                return shopadmin
        except Exception as e:
            print(e)
            return None

    def GetAdminUsernamesInDB():
        try:
            with db_lock:
                cursor.execute("SELECT username FROM ShopAdminTable")
                shopadmin =  cursor.fetchall()
                return shopadmin
        except Exception as e:
            print(e)
            return None

    def GetProductNumberName():
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT productnumber, productname FROM ShopProductTable")
                productnumbers_name = cursor.fetchall()
                if productnumbers_name is not None:
                    return productnumbers_name
                else:
                    return None
        except Exception as e:
            print(e)
            return None

    def GetProductInfos():
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT productnumber, productname, productprice FROM ShopProductTable")
                productnumbers_name = cursor.fetchall()
                if productnumbers_name is not None:
                    return productnumbers_name
                else:
                    return None
        except Exception as e:
            print(e)
            return None

    def GetProductInfo():
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory FROM ShopProductTable")
                productnumbers_name = cursor.fetchall()
                if productnumbers_name is not None:
                    return productnumbers_name
                else:
                    return None
        except Exception as e:
            print(e)
            return None

    def GetProductInfoByCTGName(productcategory):
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory FROM ShopProductTable WHERE productcategory = %s", (productcategory,))
                productnumbers_name = cursor.fetchall()
                if productnumbers_name is not None:
                    return productnumbers_name
                else:
                    return None
        except Exception as e:
            print(e)
            return None
        
    def GetProductInfoByPName(productnumber):
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory FROM ShopProductTable WHERE productnumber = %s", (productnumber,))
                productnumbers_name = cursor.fetchall()
                if productnumbers_name is not None:
                    return productnumbers_name
                else:
                    return None
        except Exception as e:
            print(e)
            return None
        
    def GetUsersInfo():
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT user_id, username, wallet FROM ShopUserTable")
                user_infos = cursor.fetchall()
                if user_infos is not None:
                    return user_infos
                else:
                    return None
        except Exception as e:
            print(e)
            return None
        
    def AllUsers():
        try:
            with db_lock:
                cursor.execute("SELECT COUNT(user_id) FROM ShopUserTable")
                alluser = cursor.fetchall()
                if alluser is not None:
                    return alluser
                else:
                    return 0
        except Exception as e:
            print(e)
            return 0
    
    def AllAdmins():
        try:
            with db_lock:
                cursor.execute("SELECT COUNT(admin_id) FROM ShopAdminTable")
                alladmin = cursor.fetchall()
                if alladmin is not None:
                    return alladmin
                else:
                    return 0
        except Exception as e:
            print(e)
            return 0

    def AllProducts():
        try:
            with db_lock:
                cursor.execute("SELECT COUNT(productnumber) FROM ShopProductTable")
                allproduct = cursor.fetchall()
                if allproduct is not None:
                    return allproduct
                else:
                    return 0
        except Exception as e:
            print(e)
            return 0

    def AllOrders():
        try:
            with db_lock:
                cursor.execute("SELECT COUNT(buyerid) FROM ShopOrderTable")
                allorder = cursor.fetchall()
                if allorder is not None:
                    return allorder
                else:
                    return 0
        except Exception as e:
            print(e)
            return 0
             
    def GetAdminsInfo():
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT admin_id, username, wallet FROM ShopAdminTable")
                admin_infos = cursor.fetchall()
                if admin_infos is not None:
                    return admin_infos
                else:
                    return None
        except Exception as e:
            print(e)
            return None
        
    def GetOrderInfo():
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT ordernumber, productname, buyerusername FROM ShopOrderTable")
                order_infos = cursor.fetchall()
                if order_infos is not None:
                    return order_infos
                else:
                    return None
        except Exception as e:
            print(e)
            return None

    def GetPaymentMethods():
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT method_name, activated, username FROM PaymentMethodTable")
                payment_method = cursor.fetchall()
                if payment_method is not None:
                    return payment_method
                else:
                    return None
        except Exception as e:
            print(e)
            return None

    def GetPaymentMethodsAll(method_name):
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT method_name, token_keys_clientid, secret_keys FROM PaymentMethodTable WHERE method_name = %s", (method_name,))
                payment_method = cursor.fetchall()
                if payment_method is not None:
                    return payment_method
                else:
                    return None
        except Exception as e:
            print(e)
            return None
 
    def GetPaymentMethodTokenKeysCleintID(method_name):
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT token_keys_clientid FROM PaymentMethodTable WHERE method_name = %s", (method_name,))
                payment_method = cursor.fetchone()[0]
                if payment_method is not None:
                    return payment_method
                else:
                    return None
        except Exception as e:
            print(e)
            return None

    def GetPaymentMethodSecretKeys(method_name):
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT secret_keys FROM PaymentMethodTable WHERE method_name = %s", (method_name,))
                payment_method = cursor.fetchone()[0]
                if payment_method is not None:
                    return payment_method
                else:
                    return None
        except Exception as e:
            print(e)
            return None

    def GetAllPaymentMethodsInDB():
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT method_name FROM PaymentMethodTable")
                payment_methods = cursor.fetchall()
                if payment_methods is not None:
                    return payment_methods
                else:
                    return None
        except Exception as e:
            print(e)
            return None
        
    def GetProductCategories():
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT productcategory FROM ShopProductTable")
                productcategory = cursor.fetchall()
                return productcategory
        except Exception as e:
            print(e)
            return "Default Category"
        
    def GetProductIDs():
        try:
            with db_lock:
                cursor.execute("SELECT productnumber FROM ShopProductTable")
                productnumbers = cursor.fetchall()
                return productnumbers
        except Exception as e:
            print(e)
            return None
    
    def GetOrderDetails(ordernumber):
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, buyercomment, ordernumber, productnumber FROM ShopOrderTable WHERE ordernumber = %s AND paidmethod != 'NO'", (ordernumber,))
                order_details = cursor.fetchall()
                if order_details is not None:
                    return order_details
                else:
                    return None
        except Exception as e:
            print(e)
            return None
        
    def GetOrderIDs_Buyer(buyerid):
        try:
            with db_lock:
                cursor.execute("SELECT ordernumber FROM ShopOrderTable WHERE buyerid = %s AND paidmethod != 'NO' ", (buyerid,))
                productnumbers = cursor.fetchall()
                return productnumbers
        except Exception as e:
            print(e)
            return None

    def GetOrderIDs():
        try:
            with db_lock:
                cursor.execute("SELECT ordernumber FROM ShopOrderTable")
                productnumbers = cursor.fetchall()
                return productnumbers
        except Exception as e:
            print(e)
            return None

    def GetAllUnfirmedOrdersUser(buyerid):
        try:
            with db_lock:
                cursor.execute("SELECT DISTINCT ordernumber, productname, buyerusername, payment_id, productnumber FROM ShopOrderTable WHERE paidmethod = 'NO' AND buyerid = %s AND payment_id != ordernumber", (buyerid,))
                payment_method = cursor.fetchall()
                if payment_method is not None:
                    return payment_method
                else:
                    return None
        except Exception as e:
            print(e)
            return None


class CleanData:
    def __init__(self) -> None:
        pass

    def CleanShopUserTable():
        try:
            with db_lock:
                cursor.execute("DELETE FROM ShopUserTable")
                db_connection.commit()
        except Exception as e:
            print(e)

    def CleanShopProductTable():
        try:
            with db_lock:
                cursor.execute("DELETE FROM ShopProductTable")
                db_connection.commit()
        except Exception as e:
            print(e)
    
    def delete_an_order(user_id, ordernumber):
        try:
            with db_lock:
                cursor.execute("DELETE FROM ShopOrderTable WHERE user_id = %s AND ordernumber = %s", (user_id, ordernumber))
                db_connection.commit()
        except Exception as e:
            print(e)

    def delete_a_product(productnumber):
        try:
            with db_lock:
                cursor.execute("DELETE FROM ShopProductTable WHERE productnumber = %s", (productnumber,))
                db_connection.commit()
        except Exception as e:
            print(e)

    def delete_an_order(ordernumber):
        try:
            with db_lock:
                cursor.execute("DELETE FROM ShopOrderTable WHERE ordernumber = %s", (ordernumber,))
                db_connection.commit()
        except Exception as e:
            print(e)

    def delete_a_payment_method(method_name):
        try:
            with db_lock:
                cursor.execute("DELETE FROM PaymentMethodTable WHERE method_name = %s", (method_name,))
                db_connection.commit()
        except Exception as e:
            print(e)

    def delete_a_category(categorynumber):
        try:
            with db_lock:
                cursor.execute("DELETE FROM ShopCategoryTable WHERE categorynumber = %s", (categorynumber,))
                db_connection.commit()
        except Exception as e:
            print(e)
