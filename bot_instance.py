import telebot
import os
from dotenv import load_dotenv

load_dotenv('config.env')

bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'), threaded=False)
store_currency = os.getenv('STORE_CURRENCY', 'USD')
