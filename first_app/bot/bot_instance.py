import telebot
from .credentials import TOKEN
from .filter import IsAdmin

API_TOKEN = TOKEN
bot = telebot.TeleBot(API_TOKEN, threaded=False)

bot.add_custom_filter(IsAdmin())
