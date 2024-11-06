import telebot
from .credentials import TOKEN


API_TOKEN = TOKEN
bot = telebot.TeleBot(API_TOKEN, threaded=False)