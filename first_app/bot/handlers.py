from telebot import types

from . import messages

from .credentials import FEEDBACK_GROUP_ID
from.bot_instance import bot
from .models import BotUser, BotGroup


user_lang = {}


def get_name(message):
    first_name = f'{message.from_user.first_name}'
    last_name = f'{message.from_user.last_name if message.from_user.last_name else None}'
    username = f'{message.from_user.username if message.from_user.username else None}'
    return {'firstname': first_name, 'lastname': last_name, 'username': username}


def welcome_buttons():
    markup = types.InlineKeyboardMarkup()
    support_btn = types.InlineKeyboardButton('Тех. поддержка', url='t.me/itsmylifestyle')
    coworking_btn = types.InlineKeyboardButton('Коворкинг', url='t.me/proweb_coworking')
    concurs_btn = types.InlineKeyboardButton('Конкурсы 🎉', callback_data='conkurs')
    webpage_btn = types.InlineKeyboardButton('Посетить сайт', url='https://www.proweb.uz')
    basic_btn = types.InlineKeyboardButton('Базовый курс', callback_data='basic_course')
    review_btn = types.InlineKeyboardButton('Оставить отзыв', callback_data='review')

    markup.row(support_btn, coworking_btn)
    markup.row(concurs_btn, webpage_btn)
    markup.row(basic_btn, review_btn)
    markup.add(types.InlineKeyboardButton('Правила обучения', callback_data='licence'))

    box_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = types.KeyboardButton('На главную')
    lang_btn = types.KeyboardButton("O'zbek tili 🇺🇿")
    box_markup.row(back_btn, lang_btn)

    return markup, box_markup


@bot.message_handler(commands=['start'])
def send_welcome(message: types.Message):
    full_name = get_name(message)



    markup, box_markup = welcome_buttons()
    bot.send_message(message.chat.id, messages.welcome_message, parse_mode='html', reply_markup=box_markup)
    bot.send_message(message.chat.id, messages.help_message, parse_mode='html', reply_markup=markup)

    bot.register_next_step_handler(message, on_click)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, messages.help_message, parse_mode='html')


@bot.message_handler(commands=['getchatid'])
def getchatid(message: types.Message):
    cid = message.chat.id
    mid = message.message_id
    fid = message.from_user.id
    bot.send_message(message.chat.id, '\n'.join([f'cid: {cid}', f'mid: {mid}', f'fid: {fid}']))


@bot.message_handler(func=lambda message: True)
def on_click(message):
    markup, _ = welcome_buttons()
    if message.text == 'На главную':
        bot.send_message(message.chat.id, messages.help_message, parse_mode='html', reply_markup=markup)
    elif message.text == "O'zbek tili 🇺🇿":
        user_lang[message.chat.id] = 'uz'
        bot.send_message(message.chat.id, "Til o'zbekchaga ogirildi")
    elif message.text == "Русккий язык 🇷🇺":
        user_lang[message.chat.id] = 'ru'
        bot.send_message(message.chat.id, "Язык изменен на русский")


@bot.callback_query_handler(func=lambda callback: callback.data == 'conkurs')
def call_concurs(callback: types.CallbackQuery):
    bot.send_message(callback.message.chat.id, messages.conkurs_message, parse_mode='html')


@bot.callback_query_handler(func=lambda callback: callback.data == 'basic_course')
def call_basic_course(callback: types.CallbackQuery):

    basic_course_markup = types.InlineKeyboardMarkup()
    bsc_btn = types.InlineKeyboardButton('Записаться на базовый курс', url='t.me/proweb_basics')

    basic_course_markup.add(bsc_btn)

    bot.send_message(callback.message.chat.id, messages.basic_course_message, parse_mode='html')
    bot.send_photo(callback.message.chat.id, open('storage/basic_course.jpg', 'rb'), reply_markup=basic_course_markup)


@bot.callback_query_handler(func=lambda callback: callback.data == 'review')
def call_review(callback: types.CallbackQuery):

    review_markup = types.InlineKeyboardMarkup()
    rvw_btn = types.InlineKeyboardButton('Отзывы 😍', url='https://proweb.uz/reviews/')
    cmp_sggtn_btn = types.InlineKeyboardButton('Жалобы и пожелания 😔', callback_data='complains_and_suggestions')
    review_markup.row(rvw_btn, cmp_sggtn_btn)

    bot.send_message(callback.message.chat.id, messages.review_message, parse_mode='html',
                     reply_markup=review_markup)


@bot.callback_query_handler(func=lambda callback: callback.data == 'licence')
def call_licence(callback: types.CallbackQuery):
    bot.send_message(callback.message.chat.id, messages.licence_message, parse_mode='html')


@bot.callback_query_handler(func=lambda callback: callback.data == 'complains_and_suggestions')
def call_complains_and_suggestions(callback: types.CallbackQuery):

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    contact_btn = types.KeyboardButton('Поделиться контактом', request_contact=True)
    keyboard.add(contact_btn)

    bot.send_message(callback.message.chat.id, messages.complain_suggestion_message, parse_mode='html',
                     reply_markup=keyboard)
    bot.register_next_step_handler(callback.message, send_contact)


@bot.message_handler(content_types=['contact', 'text'])
def send_contact(message):
    print(message)

    markup, box_markup = welcome_buttons()

    if message.content_type == 'contact':
        if message.from_user.id == message.contact.user_id:
            bot.send_message(FEEDBACK_GROUP_ID, f'User id: {message.contact.user_id}\n'
                                                f'User: @{message.from_user.username if message.from_user.username else "Нету"}\n'
                                                f'Name: {message.contact.first_name}\n'
                                                f'Phone Number: {message.contact.phone_number}')
        else:
            bot.send_message(message.from_user.id, 'Пожалуйста отправьте свой номер телефона')
    else:
        bot.send_message(FEEDBACK_GROUP_ID, f'User id: {message.from_user.id}\n'
                                            f'User: @{message.from_user.username if message.from_user.username else "Нету"}\n'
                                            f'Name: {message.from_user.first_name}\n'
                                            f'Message: {message.json["text"]}')
    text = 'Мы приняли ваш текст и постараемся обработать поскорее'
    phone = 'Мы приняли ваши данные и в скором времени свами свяжемся'
    bot.send_message(message.from_user.id, f"Спасибо за обращение!, {text if message.content_type == 'text' else phone}", reply_markup=box_markup)
    bot.send_message(message.from_user.id, messages.help_message, parse_mode='html', reply_markup=markup)