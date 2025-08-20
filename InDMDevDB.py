import sqlite3
from datetime import datetime
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_FILE = 'InDMDevDBShop.db'
db_connection = sqlite3.connect(DB_FILE, check_same_thread=False)
db_connection.row_factory = sqlite3.Row  # Enable dict-like access to rows
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
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    wallet INTEGER DEFAULT 0,
                    language TEXT DEFAULT 'en',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")
                
                # Create ShopAdminTable
                cursor.execute("""CREATE TABLE IF NOT EXISTS ShopAdminTable(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    wallet INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")

                # Create ShopProductTable
                cursor.execute("""CREATE TABLE IF NOT EXISTS ShopProductTable(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (admin_id) REFERENCES ShopAdminTable(admin_id)
                )""")

                # Create ShopOrderTable
                cursor.execute("""CREATE TABLE IF NOT EXISTS ShopOrderTable(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    payment_id TEXT,
                    FOREIGN KEY (buyerid) REFERENCES ShopUserTable(user_id),
                    FOREIGN KEY (productnumber) REFERENCES ShopProductTable(productnumber)
                )""")
                
                # Create ShopCategoryTable
                cursor.execute("""CREATE TABLE IF NOT EXISTS ShopCategoryTable(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    categorynumber INTEGER UNIQUE NOT NULL,
                    categoryname TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")
                
                # Create PaymentMethodTable
                cursor.execute("""CREATE TABLE IF NOT EXISTS PaymentMethodTable(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    "INSERT OR IGNORE INTO ShopUserTable (user_id, username, wallet) VALUES (?, ?, ?)",
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
                    "INSERT OR IGNORE INTO ShopAdminTable (admin_id, username, wallet) VALUES (?, ?, ?)",
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
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                cursor.execute("""
                    INSERT INTO ShopOrderTable 
                    (buyerid, buyerusername, productname, productprice, orderdate, 
                     paidmethod, productdownloadlink, productkeys, buyercomment, 
                     ordernumber, productnumber, payment_id) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (buyer_id, username, productname, productprice, orderdate, 
                      paidmethod, productdownloadlink, productkeys, 'NIL', 
                      ordernumber, productnumber, payment_id))
                db_connection.commit()
                logger.info(f"Order {ordernumber} added for user {username}")
                return True
        except Exception as e:
            logger.error(f"Error adding order {ordernumber}: {e}")
            db_connection.rollback()
            return False

    def AddCategory(categorynumber, categoryname):
        try:
            AddData = f"Insert into ShopCategoryTable (categorynumber, categoryname) values('{categorynumber}', '{categoryname}')"
            connected.execute(AddData)
            DBConnection.commit()
        except Exception as e:
            print(e)

    def AddEmptyRow():
        AddData = f"Insert into PaymentMethodTable (admin_id, username, method_name, activated) values('None', 'None', 'None', 'None')"
        connected.execute(AddData)
        DBConnection.commit()
    
    def AddCryptoPaymentMethod(id, username, token_keys_clientid, secret_keys, method_name):
        try:
            connected.execute(f"UPDATE PaymentMethodTable SET admin_id = ?, username = ?, token_keys_clientid = ?, secret_keys = ?, activated = 'NO' WHERE method_name = '{method_name}'", (id, username, token_keys_clientid, secret_keys))
            DBConnection.commit()
        except Exception as e:
            print(e)

    def UpdateOrderConfirmed(paidmethod, ordernumber):
        try:
            connected.execute(f"UPDATE ShopOrderTable SET paidmethod = ? WHERE ordernumber = ?", (paidmethod, ordernumber))
            DBConnection.commit()
        except Exception as e:
            print(e)

    def UpdatePaymentMethodToken(id, username, token_keys_clientid, method_name):
        try:
            connected.execute(f"UPDATE PaymentMethodTable SET admin_id = '{id}', username = '{username}', token_keys_clientid = '{token_keys_clientid}' WHERE method_name = '{method_name}'")
            DBConnection.commit()
        except Exception as e:
            print(e)

    def UpdatePaymentMethodSecret(id, username, secret_keys, method_name):
        try:
            connected.execute(f"UPDATE PaymentMethodTable SET admin_id = '{id}', username = '{username}', secret_keys = '{secret_keys}' WHERE method_name = '{method_name}'")
            DBConnection.commit()
        except Exception as e:
            print(e)

    def Update_A_Category(categoryname, categorynumber):
        try:
            connected.execute("UPDATE ShopCategoryTable SET categoryname = ? WHERE categorynumber = ?", (categoryname, categorynumber))
            DBConnection.commit()
        except Exception as e:
            print(e)

    def UpdateOrderComment(buyercomment, ordernumber):
        try:
            connected.execute(f"UPDATE ShopOrderTable SET buyercomment = ? WHERE ordernumber = ?", (buyercomment, ordernumber))
            DBConnection.commit()
        except Exception as e:
            print(e)

    def UpdateOrderPaymentMethod(paidmethod, ordernumber):
        try:
            connected.execute(f"UPDATE ShopOrderTable SET paidmethod = ? WHERE ordernumber = ?", (paidmethod, ordernumber))
            DBConnection.commit()
        except Exception as e:
            print(e)

    def UpdateOrderPurchasedKeys(productkeys, ordernumber):
        try:
            connected.execute(f"UPDATE ShopOrderTable SET productkeys = ? WHERE ordernumber = ?", (productkeys, ordernumber))
            DBConnection.commit()
        except Exception as e:
            print(e)


    def AddPaymentMethod(id, username, method_name):
        AddData = f"Insert into PaymentMethodTable (admin_id, username, method_name, activated) values('{id}', '{username}', '{method_name}', 'YES')"
        connected.execute(AddData)
        DBConnection.commit()

    def UpdateProductName(productname, productnumber):
        try:
            connected.execute(f"UPDATE ShopProductTable SET productname = ? WHERE productnumber = ?", (productname, productnumber))
            DBConnection.commit()
        except Exception as e:
            print(e)

    def UpdateProductDescription(productdescription, productnumber):
        try:
            connected.execute(f"UPDATE ShopProductTable SET productdescription = ? WHERE productnumber = ?", (productdescription, productnumber))
            DBConnection.commit()
        except Exception as e:
            print(e)
    
    def UpdateProductPrice(productprice, productnumber):
        try:
            connected.execute(f"UPDATE ShopProductTable SET productprice = ? WHERE productnumber = ?", (productprice, productnumber))
            DBConnection.commit()
        except Exception as e:
            print(e)
    
    def UpdateProductproductimagelink(productimagelink, productnumber):
        try:
            connected.execute(f"UPDATE ShopProductTable SET productimagelink = ? WHERE productnumber = ?", (productimagelink, productnumber))
            DBConnection.commit()
        except Exception as e:
            print(e)

    def UpdateProductproductdownloadlink(productdownloadlink, productnumber):
        try:
            connected.execute(f"UPDATE ShopProductTable SET productdownloadlink = ? WHERE productnumber = ?", (productdownloadlink, productnumber))
            DBConnection.commit()
        except Exception as e:
            print(e)
    
    def UpdateProductKeysFile(productkeysfile, productnumber):
        try:
            connected.execute(f"UPDATE ShopProductTable SET productkeysfile = ? WHERE productnumber = ?", (productkeysfile, productnumber))
            DBConnection.commit()
        except Exception as e:
            print(e)
    
    def UpdateProductQuantity(productquantity, productnumber):
        try:
            connected.execute(f"UPDATE ShopProductTable SET productquantity = ? WHERE productnumber = ?", (productquantity, productnumber))
            DBConnection.commit()
        except Exception as e:
            print(e)
    
    def UpdateProductCategory(productcategory, productnumber):
        try:
            connected.execute(f"UPDATE ShopProductTable SET productcategory = ? WHERE productnumber = ?", (productcategory, productnumber))
            DBConnection.commit()
        except Exception as e:
            print(e)

    def UpdateProductQuantity(productquantity, productnumber):
        try:
            connected.execute(f"UPDATE ShopProductTable SET productquantity = ? WHERE productnumber = ?", (productquantity, productnumber))
            DBConnection.commit()
        except Exception as e:
            print(e)

    def Update_All_ProductCategory(new_category, productcategory):
        try:
            connected.execute(f"UPDATE ShopProductTable SET productcategory = ? WHERE productcategory = ?", (new_category, productcategory))
            DBConnection.commit()
        except Exception as e:
            print(e)

    def update_user_language(user_id, language):
        """Update the user's language."""
        try:
            with db_lock:
                cursor.execute(
                    "UPDATE ShopUserTable SET language = ? WHERE user_id = ?",
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
                cursor.execute("SELECT wallet FROM ShopUserTable WHERE user_id = ?", (userid,))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting user wallet for {userid}: {e}")
            return 0

    def get_user_language(user_id):
        """Get the user's language from the database."""
        try:
            with db_lock:
                cursor.execute("SELECT language FROM ShopUserTable WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()
                return result[0] if result else 'en'
        except Exception as e:
            logger.error(f"Error getting language for user {user_id}: {e}")
            return 'en'
        
    def GetUserNameInDB(userid):
        try:
            connected.execute(f"SELECT username FROM ShopUserTable WHERE user_id = '{userid}'")
            shopuser = connected.fetchone()[0]
            return shopuser
        except Exception as e:
            print(e)
            return ""
        
    def GetAdminNameInDB(userid):
        try:
            connected.execute(f"SELECT username FROM ShopAdminTable WHERE admin_id = '{userid}'")
            shopuser = connected.fetchone()[0]
            return shopuser
        except Exception as e:
            print(e)
            return ""
        
    def GetUserIDsInDB():
        try:
            connected.execute(f"SELECT user_id FROM ShopUserTable")
            shopuser = connected.fetchall()
            return shopuser
        except Exception as e:
            print(e)
            return None

    def GetProductName(productnumber):
        try:
            connected.execute(f"SELECT productname FROM ShopProductTable WHERE productnumber = '{productnumber}'")
            productname = connected.fetchone()[0]
            return productname
        except Exception as e:
            print(e)
            return None

    def GetProductDescription(productnumber):
        try:
            connected.execute(f"SELECT productdescription FROM ShopProductTable WHERE productnumber = '{productnumber}'")
            productdescription = connected.fetchone()[0]
            return productdescription
        except Exception as e:
            print(e)
            return None

    def GetProductPrice(productnumber):
        try:
            connected.execute(f"SELECT productprice FROM ShopProductTable WHERE productnumber = '{productnumber}'")
            productprice = connected.fetchone()[0]
            return productprice
        except Exception as e:
            print(e)
            return None
        
    def GetProductImageLink(productnumber):
        try:
            connected.execute(f"SELECT productimagelink FROM ShopProductTable WHERE productnumber = '{productnumber}'")
            productimagelink = connected.fetchone()[0]
            return productimagelink
        except Exception as e:
            print(e)
            return None
    
    def GetProductDownloadLink(productnumber):
        try:
            connected.execute(f"SELECT productdownloadlink FROM ShopProductTable WHERE productnumber = '{productnumber}'")
            productimagelink = connected.fetchone()[0]
            return productimagelink
        except Exception as e:
            print(e)
            return None

    def GetProductNumber(productnumber):
        try:
            connected.execute(f"SELECT productnumber FROM ShopProductTable WHERE productnumber = '{productnumber}'")
            productnumbers = connected.fetchone()[0]
            return productnumbers
        except Exception as e:
            print(e)
            return None

    def GetProductQuantity(productnumber):
        try:
            connected.execute(f"SELECT productquantity FROM ShopProductTable WHERE productnumber = '{productnumber}'")
            productprice = connected.fetchone()[0]
            return productprice
        except Exception as e:
            print(e)
            return None

    def GetProduct_A_Category(productnumber):
        try:
            connected.execute(f"SELECT productcategory FROM ShopProductTable WHERE productnumber = '{productnumber}'")
            productcategory = connected.fetchone()[0]
            return productcategory
        except Exception as e:
            print(e)
            return None

    def Get_A_CategoryName(categorynumber):
        try: 
            connected.execute(f"SELECT DISTINCT categoryname FROM ShopCategoryTable WHERE categorynumber = '{categorynumber}'")
            productcategory = connected.fetchone()[0]
            if productcategory is not None:
                return productcategory    
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def GetCategoryIDsInDB():
        try:
            connected.execute(f"SELECT categorynumber, categoryname FROM ShopCategoryTable")
            categories =  connected.fetchall()
            if categories is not None:
                return categories
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def GetCategoryNumProduct(productcategory):
        try:
            connected.execute(f"SELECT COUNT(*) FROM ShopProductTable WHERE productcategory = '{productcategory}'")
            categories =  connected.fetchall()
            if categories is not None:
                return categories
            else:
                return None
        except Exception as e:
            print(e)
            return None
        
    def GetProduct_A_AdminID(productnumber):
        try:
            connected.execute(f"SELECT admin_id FROM ShopProductTable WHERE productnumber = '{productnumber}'")
            productcategory = connected.fetchone()[0]
            return productcategory
        except Exception as e:
            print(e)
            return None

    def GetAdminIDsInDB():
        try:
            connected.execute(f"SELECT admin_id FROM ShopAdminTable")
            shopadmin =  connected.fetchall()
            return shopadmin
        except Exception as e:
            print(e)
            return None

    def GetAdminUsernamesInDB():
        try:
            shopadmin = []
            connected.execute(f"SELECT username FROM ShopAdminTable")
            shopadmin =  connected.fetchall()
            return shopadmin
        except Exception as e:
            print(e)
            return None

    def GetProductNumberName():
        try:
            productnumbers_name = []
            connected.execute(f"SELECT DISTINCT productnumber, productname FROM ShopProductTable")
            productnumbers_name = connected.fetchall()
            if productnumbers_name is not None:
                return productnumbers_name
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def GetProductInfos():
        try:
            productnumbers_name = []
            connected.execute(f"SELECT DISTINCT productnumber, productname, productprice FROM ShopProductTable")
            productnumbers_name = connected.fetchall()
            if productnumbers_name is not None:
                return productnumbers_name
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def GetProductInfo():
        try:
            productnumbers_name = []
            connected.execute(f"SELECT DISTINCT productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory FROM ShopProductTable")
            productnumbers_name = connected.fetchall()
            if productnumbers_name is not None:
                return productnumbers_name
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def GetProductInfoByCTGName(productcategory):
        try:
            productnumbers_name = []
            connected.execute(f"SELECT DISTINCT productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory FROM ShopProductTable WHERE productcategory = '{productcategory}'")
            productnumbers_name = connected.fetchall()
            if productnumbers_name is not None:
                return productnumbers_name
            else:
                return None
        except Exception as e:
            print(e)
            return None
        
    def GetProductInfoByPName(productnumber):
        try:
            productnumbers_name = []
            connected.execute(f"SELECT DISTINCT productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory FROM ShopProductTable WHERE productnumber = '{productnumber}'")
            productnumbers_name = connected.fetchall()
            if productnumbers_name is not None:
                return productnumbers_name
            else:
                return None
        except Exception as e:
            print(e)
            return None
        
    def GetUsersInfo():
        try:
            user_infos = []
            connected.execute(f"SELECT DISTINCT user_id, username, wallet FROM ShopUserTable")
            user_infos = connected.fetchall()
            if user_infos is not None:
                return user_infos
            else:
                return None
        except Exception as e:
            print(e)
            return None
        
    def AllUsers():
        try:
            connected.execute(f"SELECT COUNT(user_id) FROM ShopUserTable")
            alluser = connected.fetchall()
            if alluser is not None:
                return alluser
            else:
                return 0
        except Exception as e:
            print(e)
            return 0
    
    def AllAdmins():
        try:
            connected.execute(f"SELECT COUNT(admin_id) FROM ShopAdminTable")
            alladmin = connected.fetchall()
            if alladmin is not None:
                return alladmin
            else:
                return 0
        except Exception as e:
            print(e)
            return 0

    def AllProducts():
        try:
            connected.execute(f"SELECT COUNT(productnumber) FROM ShopProductTable")
            allproduct = connected.fetchall()
            if allproduct is not None:
                return allproduct
            else:
                return 0
        except Exception as e:
            print(e)
            return 0

    def AllOrders():
        try:
            connected.execute(f"SELECT COUNT(buyerid) FROM ShopOrderTable")
            allorder = connected.fetchall()
            if allorder is not None:
                return allorder
            else:
                return 0
        except Exception as e:
            print(e)
            return 0
             
    def GetAdminsInfo():
        try:
            admin_infos = []
            connected.execute(f"SELECT DISTINCT admin_id, username, wallet FROM ShopAdminTable")
            admin_infos = connected.fetchall()
            if admin_infos is not None:
                return admin_infos
            else:
                return None
        except Exception as e:
            print(e)
            return None
        
    def GetOrderInfo():
        try:
            order_infos = []
            connected.execute(f"SELECT DISTINCT ordernumber, productname, buyerusername FROM ShopOrderTable")
            order_infos = connected.fetchall()
            if order_infos is not None:
                return order_infos
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def GetPaymentMethods():
        try:
            payment_method = []
            connected.execute(f"SELECT DISTINCT method_name, activated, username FROM PaymentMethodTable")
            payment_method = connected.fetchall()
            if payment_method is not None:
                return payment_method
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def GetPaymentMethodsAll(method_name):
        try:
            payment_method = []
            connected.execute(f"SELECT DISTINCT method_name, token_keys_clientid, secret_keys FROM PaymentMethodTable WHERE method_name = '{method_name}'")
            payment_method = connected.fetchall()
            if payment_method is not None:
                return payment_method
            else:
                return None
        except Exception as e:
            print(e)
            return None
 
    def GetPaymentMethodTokenKeysCleintID(method_name):
        try:
            connected.execute(f"SELECT DISTINCT token_keys_clientid FROM PaymentMethodTable WHERE method_name = '{method_name}'")
            payment_method = connected.fetchone()[0]
            if payment_method is not None:
                return payment_method
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def GetPaymentMethodSecretKeys(method_name):
        try:
            connected.execute(f"SELECT DISTINCT secret_keys FROM PaymentMethodTable WHERE method_name = '{method_name}'")
            payment_method = connected.fetchone()[0]
            if payment_method is not None:
                return payment_method
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def GetAllPaymentMethodsInDB():
        try:
            payment_methods = []
            connected.execute(f"SELECT DISTINCT method_name FROM PaymentMethodTable")
            payment_methods = connected.fetchall()
            if payment_methods is not None:
                return payment_methods
            else:
                return None
        except Exception as e:
            print(e)
            return None
        
    def GetProductCategories():
        try:
            productcategory = []
            connected.execute(f"SELECT DISTINCT productcategory FROM ShopProductTable")
            productcategory = connected.fetchall()
            return productcategory
        except Exception as e:
            print(e)
            return "Default Category"
        
    def GetProductIDs():
        try:
            productnumbers = []
            connected.execute(f"SELECT productnumber FROM ShopProductTable")
            productnumbers = connected.fetchall()
            return productnumbers
        except Exception as e:
            print(e)
            return None
    
    def GetOrderDetails(ordernumber):
        try:
            order_details = []
            connected.execute(f"SELECT DISTINCT buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, buyercomment, ordernumber, productnumber FROM ShopOrderTable WHERE ordernumber = '{ordernumber}' AND paidmethod != 'NO'")
            order_details = connected.fetchall()
            if order_details is not None:
                return order_details
            else:
                return None
        except Exception as e:
            print(e)
            return None
        
    def GetOrderIDs_Buyer(buyerid):
        try:
            productnumbers = []
            connected.execute(f"SELECT ordernumber FROM ShopOrderTable WHERE buyerid = '{buyerid}' AND paidmethod != 'NO' ")
            productnumbers = connected.fetchall()
            return productnumbers
        except Exception as e:
            print(e)
            return None

    def GetOrderIDs():
        try:
            productnumbers = []
            connected.execute(f"SELECT ordernumber FROM ShopOrderTable")
            productnumbers = connected.fetchall()
            return productnumbers
        except Exception as e:
            print(e)
            return None

    def GetAllUnfirmedOrdersUser(buyerid):
        try:
            payment_method = []
            connected.execute(f"SELECT DISTINCT ordernumber, productname, buyerusername, payment_id, productnumber FROM ShopOrderTable WHERE paidmethod = 'NO' AND buyerid = '{buyerid}' AND payment_id != ordernumber")
            payment_method = connected.fetchall()
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
            connected.execute("DELETE FROM ShopUserTable")
            DBConnection.commit()
        except Exception as e:
            print(e)

    def CleanShopProductTable():
        try:
            connected.execute("DELETE FROM ShopProductTable")
            DBConnection.commit()
        except Exception as e:
            print(e)
    
    def delete_an_order(user_id, ordernumber):
        try:
            connected.execute(f"DELETE FROM ShopOrderTable WHERE user_id = '{user_id}' AND ordernumber = '{ordernumber}'")
            DBConnection.commit()
        except Exception as e:
            print(e)

    def delete_a_product(productnumber):
        try:
            connected.execute(f"DELETE FROM ShopProductTable WHERE productnumber = '{productnumber}'")
            DBConnection.commit()
        except Exception as e:
            print(e)

    def delete_an_order(ordernumber):
        try:
            connected.execute(f"DELETE FROM ShopOrderTable WHERE ordernumber = '{ordernumber}'")
            DBConnection.commit()
        except Exception as e:
            print(e)

    def delete_a_payment_method(method_name):
        try:
            connected.execute(f"DELETE FROM PaymentMethodTable WHERE method_name = '{method_name}'")
            DBConnection.commit()
        except Exception as e:
            print(e)

    def delete_a_category(categorynumber):
        try:
            connected.execute(f"DELETE FROM ShopCategoryTable WHERE categorynumber = '{categorynumber}'")
            DBConnection.commit()
        except Exception as e:
            print(e)







