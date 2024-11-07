from telebot import types
import telebot

from . import messages

from .bot_instance import bot
from .models import BotUser, BotGroup


class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_admin'

    @staticmethod
    def check(message: telebot.types.Message):
        user = BotUser.objects.get(chat_id=message.chat.id)
        return True if user.role == 'admin' else False


def send_admin_conf(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton('Да', callback_data=f'conf_{chat_id}')
    no_btn = types.InlineKeyboardButton('Нет', callback_data=f'deny_{chat_id}')
    keyboard.add(yes_btn, no_btn)

    bot.send_message(chat_id, 'Vy gotovy stat\' adminom proweb bota?', reply_markup=keyboard)


@bot.callback_query_handler(
    func=lambda callback: callback.data.startswith('conf_') or callback.data.startswith('deny_'))
def admin_conf(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)

    if callback.data.startswith('conf_'):
        user.role = 'admin'
        user.save()
        bot.send_message(chat_id, 'Теперь вы администратор бота')
        admin_panel(chat_id)
    else:
        user.role = 'normal'
        user.save()
        bot.send_message(chat_id, 'Вы отказались от админства')


def admin_panel(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    users_btn = types.KeyboardButton('Отправить')
    groups_btn = types.KeyboardButton('Переслать')
    keyboard.add(users_btn, groups_btn)

    bot.send_message(message.chat.id, 'Админ панель', reply_markup=keyboard)
    bot.register_next_step_handler(message, on_click_admin)


@bot.message_handler(is_admin=True, func=lambda message: message.text == 'Отправить' or message.text == 'Переслать')
def on_click_admin(message: types.Message):
    print(message.text)

    if message.text == 'Отправить':
        course_lang(message)
    elif message.text == 'Переслать':
        course_lang(message)
    else:
        admin_panel(message)


def course_lang(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    course_btn = types.KeyboardButton('Курс')
    language_btn = types.KeyboardButton('Язык')
    keyboard.row(course_btn, language_btn)

    bot.send_message(message.chat.id, ' По чему фильтруем?', reply_markup=keyboard)
    bot.register_next_step_handler(message, on_click_course_lang)


@bot.message_handler(is_admin=True, func=lambda message: message.text == 'Курс' or message.text == 'Язык')
def on_click_course_lang(message: types.Message):
    groups = BotGroup.objects.all()
    users = BotUser.objects.all()
    if message.text == 'Курс':
        for group in users:
            bot.send_message(message.chat.id, group.first_name)
    elif message.text == 'Язык':
        for group in users:
            bot.send_message(message.chat.id, group.last_name)
    else:
        course_lang(message)


bot.add_custom_filter(IsAdmin())