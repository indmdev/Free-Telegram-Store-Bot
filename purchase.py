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


# M""M M"""""""`YM M""""""'YMM M"""""`'"""`YM M""""""'YMM MM""""""""`M M""MMMMM""M 
# M  M M  mmmm.  M M  mmmm. `M M  mm.  mm.  M M  mmmm. `M MM  mmmmmmmM M  MMMMM  M 
# M  M M  MMMMM  M M  MMMMM  M M  MMM  MMM  M M  MMMMM  M M`      MMMM M  MMMMP  M 
# M  M M  MMMMM  M M  MMMMM  M M  MMM  MMM  M M  MMMMM  M MM  MMMMMMMM M  MMMM' .M 
# M  M M  MMMMM  M M  MMMM' .M M  MMM  MMM  M M  MMMM' .M MM  MMMMMMMM M  MMP' .MM 
# M  M M  MMMMM  M M       .MM M  MMM  MMM  M M       .MM MM        .M M     .dMMM 
# MMMM MMMMMMMMMMM MMMMMMMMMMM MMMMMMMMMMMMMM MMMMMMMMMMM MMMMMMMMMMMM MMMMMMMMMMM 

from bot_instance import bot, store_currency

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

    #@bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        if call.data == "check":
            check_command(call.message)
        else:
            print("Ok")

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
