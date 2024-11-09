from telebot import types
import telebot

from . import messages

from .bot_instance import bot
from .models import BotUser, BotGroup

selected_courses = {}


class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_admin'

    @staticmethod
    def check(message: telebot.types.Message):
        try:
            user = BotUser.objects.get(chat_id=message.chat.id)
        except BotUser.DoesNotExist:
            return False
        return True if user.role == 'admin' else False


def send_admin_conf(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton('Да', callback_data=f'conf_{chat_id}')
    no_btn = types.InlineKeyboardButton('Нет', callback_data=f'deny_{chat_id}')
    keyboard.add(yes_btn, no_btn)

    bot.send_message(chat_id, 'Вы готовы стать админом ПРОВЕБ бота?', reply_markup=keyboard)


@bot.callback_query_handler(
    func=lambda callback: callback.data.startswith('conf_') or callback.data.startswith('deny_'))
def admin_conf(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)

    if callback.data.startswith('conf_'):
        user.role = 'admin'
        user.save()
        bot.send_message(chat_id, 'Теперь вы администратор бота')
        admin_panel(callback.message)
    else:
        user.role = 'normal'
        user.save()
        bot.send_message(chat_id, 'Вы отказались от админства')

    bot.answer_callback_query(callback_query_id=callback.id)


@bot.message_handler(commands=['start'], chat_types=['private'], is_admin=True)
def start(message: types.Message):
    admin_panel(message)


def admin_panel(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    users_btn = types.KeyboardButton('Отправить')
    groups_btn = types.KeyboardButton('Переслать')
    keyboard.add(users_btn, groups_btn)

    bot.send_message(message.chat.id, 'Админ панель', reply_markup=keyboard)
    bot.register_next_step_handler(message, on_click_admin)


@bot.message_handler(is_admin=True, func=lambda message: message.text == 'Отправить' or message.text == 'Переслать')
def on_click_admin(message: types.Message):
    if message.text == 'Отправить':
        lang_select(message)
    elif message.text == 'Переслать':
        lang_select(message)
    else:
        admin_panel(message)


def lang_select(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ru_btn = types.KeyboardButton('РУС')
    uz_btn = types.KeyboardButton('УЗБ')
    all_btn = types.KeyboardButton('Все')
    keyboard.row(ru_btn, uz_btn)
    keyboard.add(all_btn)

    bot.send_message(message.chat.id, ' Язык?', reply_markup=keyboard)
    bot.register_next_step_handler(message, lang_handle)


@bot.message_handler(is_admin=True, func=lambda message: message.text in ['РУС', 'УЗБ', 'Все'])
def lang_handle(message: types.Message):
    if message.text == 'Все':
        groups = BotGroup.objects.all()
    else:
        groups = BotGroup.objects.filter(group_language=message.text)
    course_select(message, groups)


def create_inline_kb(kbs, id_chat, lang):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for inline in kbs:
        text = f'✔️ {inline}' if inline in selected_courses else inline
        print(text)
        keyboard.add(types.InlineKeyboardButton(text, callback_data=f'select_{inline}_{lang}'))
    keyboard.add(types.InlineKeyboardButton('All', callback_data=f'select_All_{lang}'))
    keyboard.add(types.InlineKeyboardButton('✅ Подтвердить', callback_data='confirm'))
    bot.send_message(id_chat, 'Выбирайте', reply_markup=keyboard)


def course_select(message: types.Message, groups):
    group_filter_by_course = set()

    for group in groups:
        if group.course_name not in group_filter_by_course:
            group_filter_by_course.add(group.course_name)
    create_inline_kb(group_filter_by_course, message.chat.id, message.text)


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_') or call.data == 'confirm')
def multiple_selection(call: types.CallbackQuery):
    chat_id = call.message.chat.id

    if call.data != 'confirm':
        msg = call.data[7:]
        course, lang = msg.split('_', 2)

        if chat_id not in selected_courses:
            selected_courses[chat_id] = []
        if course in selected_courses[chat_id]:
            selected_courses[chat_id].remove(course)
        else:
            selected_courses[chat_id].append(course)

        print(selected_courses)
    else:
        if 'All' in selected_courses[chat_id]:
            selected_courses[chat_id] = ['All']
            bot.send_message(chat_id, f'Принял ваш запрос. Что вы хотите отправить во все группы')
        else:
            bot.send_message(chat_id, f'Принял ваш запрос. Что вы хотите отправить в группу(ы) {", ".join(selected_courses[chat_id])}')

        del selected_courses[chat_id]
        bot.register_next_step_handler(call.message, get_messages)

    bot.answer_callback_query(callback_query_id=call.id)


@bot.message_handler(is_admin=True, content_types=['text', 'audio', 'video', 'image', 'photo', 'voice', 'document'], func=lambda message: True)
def get_messages(message: types.Message):
    bot.send_message(message.chat.id, message.text)





bot.add_custom_filter(IsAdmin())