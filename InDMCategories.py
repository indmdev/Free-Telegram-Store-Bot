

from datetime import *
from flask_session import Session
import telebot
from flask import Flask, request
from telebot import types
import os
import os.path
from InDMDevDB import *
from dotenv import load_dotenv
load_dotenv('config.env')

# Bot connection
bot = telebot.TeleBot(f"{os.getenv('TELEGRAM_BOT_TOKEN')}", threaded=False)
StoreCurrency = f"{os.getenv('STORE_CURRENCY')}"

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
                    key1 = types.KeyboardButton(text="Shop Items 🛒")
                    key2 = types.KeyboardButton(text="My Orders 🛍")
                    key3 = types.KeyboardButton(text="Support 📞")
                    keyboard.add(key1)
                    keyboard.add(key2, key3)
                    bot.send_message(id, f"No Product in the store", reply_markup=keyboard)
                else:
                    bot.send_message(id, f"{product_cate} Gategory's Products")
                    keyboard = types.InlineKeyboardMarkup()
                    for productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory in product_list:
                        keyboard.add(types.InlineKeyboardButton(text="BUY NOW 💰", callback_data=f"getproduct_{productnumber}"))
                        bot.send_photo(id, photo=f"{productimagelink}", caption=f"Product ID 🪪: /{productnumber}\n\nProduct Name 📦: {productname}\n\nProduct Price 💰: {productprice} {StoreCurrency}\n\nProducts In Stock 🛍: {productquantity}\n\nProduct Description 💬: {productdescription}", reply_markup=keyboard)
                        
                        #bot.send_message(id, "💡 Click on a Product ID to select the product purchase")
            else:
                print("Wrong commmand !!!")
