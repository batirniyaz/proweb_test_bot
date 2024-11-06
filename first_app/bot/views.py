import json

import telebot
from telebot import types
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST
from . import messages

from .credentials import TOKEN, NGROK_URL

API_TOKEN = TOKEN

bot = telebot.TeleBot(API_TOKEN, threaded=False)
WEBHOOK_PATH = f'bot/{TOKEN}'
WEBHOOK_URL = f'{NGROK_URL}/{WEBHOOK_PATH}/'

bot.set_webhook(
    url=WEBHOOK_URL
)


def main_view(request):
    response = JsonResponse({'ok': True, 'result': True, 'method': request.method})
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    # response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"

    return response


@require_POST
def api_bots(request: HttpRequest, token):
    """ main function """

    method = request.method
    data_unicode = request.body.decode('utf-8')

    if data_unicode is None or data_unicode == '':
        return JsonResponse({'error': True, 'method': method})

    data = json.loads(data_unicode)
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])

    return main_view(request)

user_lang = {'ru'}


@bot.message_handler(commands=['start'])
def send_welcome(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    support_btn = types.InlineKeyboardButton('Тех. поддержка' if user_lang == 'ru' else 'Texnik Yordam', url='t.me/itsmylifestyle')
    coworking_btn = types.InlineKeyboardButton('Коворкинг', url='t.me/proweb_coworking')
    concurs_btn = types.InlineKeyboardButton('Конкурсы', callback_data='conkurs')
    webpage_btn = types.InlineKeyboardButton('Посетить сайт', url='https://www.proweb.uz')
    basic_btn = types.InlineKeyboardButton('Базовый курс', callback_data='basic_course')
    review_btn = types.InlineKeyboardButton('Оставить отзыв', callback_data='review')

    markup.row(support_btn, coworking_btn)
    markup.row(concurs_btn, webpage_btn)
    markup.row(basic_btn, review_btn)
    markup.add(types.InlineKeyboardButton('Правила обучения', callback_data='licence'))

    box_markup = types.ReplyKeyboardMarkup()
    back_btn = types.KeyboardButton('На главную')
    lang_btn = types.KeyboardButton("O'zbek tili")
    box_markup.row(back_btn, lang_btn)

    bot.send_message(message.chat.id, messages.welcome_message, parse_mode='html', reply_markup=box_markup)
    bot.send_message(message.chat.id, messages.help_message, parse_mode='html', reply_markup=markup)

    bot.register_next_step_handler(message, on_click)


def on_click(message):
    if message.text == 'На главную':
        bot.send_message(message.chat.id, messages.help_message)
    elif message.text == "O'zbek tili":
        user_lang[message.chat.id] = 'uz'
        bot.send_message(message.chat.id, "Til o'zbekchaga ogirildi")
    elif message.text == "Русский язык":
        user_lang[message.chat.id] = 'ru'
        bot.send_message(message.chat.id, "Язык изменен на русский")


@bot.callback_query_handler(func=lambda callback: True)
def call_messages(callback: types.CallbackQuery):
    basic_course_markup = types.InlineKeyboardMarkup()
    bsc_btn = types.InlineKeyboardButton('Записаться на базовый курс', url='t.me/proweb_basics')

    basic_course_markup.add(bsc_btn)

    review_markup = types.InlineKeyboardMarkup()
    rvw_btn = types.InlineKeyboardButton('Отзывы', url='https://proweb.uz/reviews/')
    cmp_sggtn_btn = types.InlineKeyboardButton('Жалобы и пожелания', callback_data='complains_and_suggestions')
    review_markup.row(rvw_btn, cmp_sggtn_btn)

    if callback.data == 'conkurs':
        file = open('storage/conkurs.jpg', 'rb')
        bot.send_photo(callback.message.chat.id, file, caption=messages.conkurs_message, parse_mode='html')
        # bot.send_message(callback.message.chat.id, messages.conkurs_message, parse_mode='html')
    elif callback.data == 'basic_course':
        bot.send_message(callback.message.chat.id, messages.basic_course_message, parse_mode='html')
        bot.send_photo(callback.message.chat.id, open('storage/basic_course.jpg', 'rb'), reply_markup=basic_course_markup, caption_entities=messages.basic_course_message)
    elif callback.data == 'review':
        bot.send_message(callback.message.chat.id, messages.review_message, parse_mode='html',
                         reply_markup=review_markup)
    elif callback.data == 'licence':
        bot.send_message(callback.message.chat.id, messages.licence_message, parse_mode='html')


def callback_review(callback: types.CallbackQuery):
    print(f"{callback.data=}")
    if callback.data == 'complains_and_suggestions':
        bot.send_message(callback.message.chat.id, messages.complain_suggestion_message, parse_mode='html')


# @bot.callback_query_handler(func=lambda callback: True)
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, messages.help_message, parse_mode='html')


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)
