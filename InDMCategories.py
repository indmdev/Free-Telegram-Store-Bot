

from datetime import *
from flask_session import Session
import telebot
from flask import Flask, request
from telebot import types
import os
import os.path
from InDMDevDB import *
from localization import get_text
from utils import create_main_keyboard

from bot_instance import bot, store_currency

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
                        
                        #bot.send_message(id, "💡 Click on a Product ID to select the product purchase")
            else:
                print(get_text(id, 'wrong_command'))
