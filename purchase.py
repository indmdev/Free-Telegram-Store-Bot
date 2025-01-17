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

class UserOperations:
    def shop_items(message):
        id = message.from_user.id
        usname = message.chat.username
        products_list = GetDataFromDB.GetProductInfo()
        id = message.from_user.id
        all_categories = GetDataFromDB.GetCategoryIDsInDB()
        keyboard = types.InlineKeyboardMarkup()
        if all_categories == []:
            bot.send_message(id, "⚠️ No Product available at the moment, kindly check back soon ")
        else:
            for catnum, catname in all_categories:
                c_catname = catname.upper()
                products_category = GetDataFromDB.GetCategoryNumProduct(c_catname)
                for ctg in products_category:
                    products_in_category = ctg[0]
                    text_but = f"🏷 {catname} ({products_in_category})"
                    text_cal = f"getcats_{catnum}"
                    keyboard.add(types.InlineKeyboardButton(text=text_but, callback_data=text_cal))
        

            bot.send_message(id, f"CATEGORIES:", reply_markup=keyboard)
            bot.send_message(id, "List completed ✅", reply_markup=types.ReplyKeyboardRemove())
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
                key1 = types.KeyboardButton(text="Bitcoin ฿")
                keyboard.add(key1)
                for productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory in product_list:
                    list_m =  [productnumber, productname, productprice, productdescription, productimagelink, productdownloadlink, productquantity, productcategory]
                    bot.send_message(id, "💡 Select a Payment method to pay for this product 👇", reply_markup=keyboard)
                global order_info
                order_info = list_m
            else:
                print("Wrong command !!!")
    def orderdata():
        try:
            1==1
            print(order_info)
            return  order_info
        except:
            return None
