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


def admin_panel(message):
    chat_id = message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    users_btn = types.InlineKeyboardButton('Пользователи', callback_data='users')
    groups_btn = types.InlineKeyboardButton('Группы', callback_data='groups')
    keyboard.add(users_btn, groups_btn)

    bot.send_message(chat_id, 'Админ панель', reply_markup=keyboard)

    bot.register_next_step_handler(message, on_click_admin)


@bot.message_handler(func=lambda message: True)
def on_click_admin(message):
    if message.text == 'Пользователи':
        users = BotUser.objects.all()
        for user in users:
            bot.send_message(message.chat.id, user.username)
    elif message.text == 'Группы':
        groups = BotGroup.objects.all()
        for group in groups:
            bot.send_message(message.chat.id, group.chat_link or group.chat_name)
    else:
        admin_panel(message.chat.id)
