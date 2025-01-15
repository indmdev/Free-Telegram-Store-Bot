import sqlite3
from datetime import *
import threading

InDMDevDBShopDBFile = 'InDMDevDBShop.db'
DBConnection = sqlite3.connect(InDMDevDBShopDBFile, check_same_thread=False)

connected = DBConnection.cursor()
lock = threading.Lock()

class CreateTables:
    def __init__(self) -> None:
        pass

    def createtable():
        #Create ShopUserTable Table
        connected.execute("""CREATE TABLE IF NOT EXISTS ShopUserTable(
                id SERIAL PRIMARY KEY,
                user_id int,
                username text,
                wallet int
            )""")
        #Create ShopAdminTable Table
        connected.execute("""CREATE TABLE IF NOT EXISTS ShopAdminTable(
                id SERIAL PRIMARY KEY,
                admin_id int,
                username text,
                wallet int
        )""")

        #Create ShopProductTable Table
        connected.execute("""CREATE TABLE IF NOT EXISTS ShopProductTable(
                id SERIAL PRIMARY KEY,
                productnumber int,
                admin_id int,
                username text,
                productname text,
                productdescription text,
                productprice int,
                productimagelink text,
                productdownloadlink text,
                productkeysfile text,
                productquantity int,
                productcategory text
        )""")

        #Create ShopOrderTable Table
        connected.execute("""CREATE TABLE IF NOT EXISTS ShopOrderTable(
                id SERIAL PRIMARY KEY,
                buyerid int,
                buyerusername text,
                productname text,
                productprice text,
                orderdate int,
                paidmethod text,
                productdownloadlink text,
                productkeys text,
                buyercomment text,
                ordernumber int,
                productnumber int,
                payment_id int

 
        )""")
        connected.execute("""CREATE TABLE IF NOT EXISTS ShopCategoryTable(
                id SERIAL PRIMARY KEY,
                categorynumber int,
                categoryname text
        )""")
        #Create PaymentMethodTable Table
        connected.execute("""CREATE TABLE IF NOT EXISTS PaymentMethodTable(
                id SERIAL PRIMARY KEY,
                admin_id int,
                username text,
                method_name text,
                token_keys_clientid text,
                secret_keys text,
                activated text
        )""")
        
CreateTables.createtable()

class CreateDatas:
    def __init__(self) -> None:
        pass

    def AddAuser(id, username):
        try:
            AddData = f"Insert into ShopUserTable (user_id, username, wallet)values('{id}','{username}', '0')"
            connected.execute(AddData)
            DBConnection.commit()
        except Exception as e:
            print(e)
            
    def AddAdmin(id, username):
        try:
            AddData = f"Insert into ShopAdminTable (admin_id, username, wallet) values('{id}', '{username}', '0')"
            connected.execute(AddData)
            DBConnection.commit()
        except Exception as e:
            print(e)

    def AddProduct(productnumber, id, username):
        try:
            AddData = f"Insert into ShopProductTable (productnumber, admin_id, username, productname, productdescription, productprice, productimagelink, productdownloadlink, productkeysfile, productquantity, productcategory) values('{productnumber}', '{id}', '{username}', 'NIL', 'NIL', '0', 'NIL', 'https://nil.nil', 'NIL', '0', 'Default Category')"
            connected.execute(AddData)
            DBConnection.commit()
        except Exception as e:
            print(e)

    def AddOrder(id, username,productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, ordernumber, productnumber, payment_id):
        try:
            AddData = f"Insert into ShopOrderTable (buyerid, buyerusername, productname, productprice, orderdate, paidmethod, productdownloadlink, productkeys, buyercomment, ordernumber, productnumber, payment_id) values('{id}', '{username}', '{productname}', '{productprice}', '{orderdate}', '{paidmethod}', '{productdownloadlink}', '{productkeys}', 'NIL', '{ordernumber}', '{productnumber}', '{payment_id}')"
            connected.execute(AddData)
            DBConnection.commit()
        except Exception as e:
            print(e)

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

class GetDataFromDB:
    def __init__(self) -> None:
        pass

    def GetUserWalletInDB(userid):
        try:
            connected.execute(f"SELECT wallet FROM ShopUserTable WHERE user_id = '{userid}'")
            shopuser = connected.fetchone()[0]
            return shopuser
        except Exception as e:
            print(e)
            return ""
        
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







