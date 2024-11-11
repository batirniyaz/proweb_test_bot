from telebot import types
from telebot.types import InputMediaPhoto, InputMediaVideo

from .bot_instance import bot
from .models import BotUser, BotGroup

admin_selection = {}


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
        bot.delete_message(chat_id, message_id=callback.message.message_id)
        bot.send_message(chat_id, 'Теперь вы администратор бота')
        admin_panel(callback.message)
    elif callback.data.startswith('deny_'):
        user.role = 'normal'
        user.save()
        bot.delete_message(chat_id, message_id=callback.message.message_id)
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
    cid = message.chat.id
    admin_selection.setdefault(cid, [{'command': ''}, {'language': ''}, {'courses': []}, {'messages': []}])
    admin_selection[cid][0]['command'] = message.text
    print(admin_selection)
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
    keyboard.row(ru_btn, uz_btn, all_btn)
    keyboard.add(types.KeyboardButton('Отменить'))

    bot.send_message(message.chat.id, ' Язык?', reply_markup=keyboard)
    bot.register_next_step_handler(message, lang_handle)


def groups_by_lang(m: types.Message):
    if m.text == 'Все':
        groups = BotGroup.objects.all()
    else:
        groups = BotGroup.objects.filter(group_language=m.text)
    return groups


@bot.message_handler(is_admin=True,
                     func=lambda message: message.text in ['РУС', 'УЗБ', 'Все', 'Отменить'])
def lang_handle(message: types.Message):
    cid = message.chat.id
    if message.text != 'Отменить':
        admin_selection[cid][1]['language'] = message.text
        print(admin_selection)
        groups = groups_by_lang(message)
        course_select(message, groups)
    else:
        if cid in admin_selection:
            del admin_selection[cid]
        admin_panel(message)


def create_inline_kb(kbs, chat_id, lang):
    keyboard = types.InlineKeyboardMarkup()
    selected = admin_selection[chat_id][2]['courses']

    for inline in kbs:
        text = f'🟢 {inline}' if inline in selected else inline
        keyboard.add(types.InlineKeyboardButton(text, callback_data=f'select_{inline}_{lang}'))

    all_text = '🟢 All' if 'All' in selected else 'All'
    keyboard.add(types.InlineKeyboardButton(all_text, callback_data=f'select_All_{lang}'))
    keyboard.add(types.InlineKeyboardButton('✅ Подтвердить', callback_data='confirm'))

    return keyboard


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_') or call.data == 'confirm')
def multiple_selection(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    selected = admin_selection[chat_id][2]['courses']

    if call.data != 'confirm':
        msg = call.data[7:]
        course, lang = msg.split('_', 2)

        if course == 'All':
            if 'All' in selected:
                selected.clear()
            else:
                selected.clear()
                selected.append('All')
        else:
            if 'All' in selected:
                selected.remove('All')

            if course in selected:
                selected.remove(course)
            else:
                selected.append(course)

        text = (f'Выберите курс\n\nВыбранные курсы: {", ".join(selected)}' if selected else 'Выберите курс')

        call.message.text = lang
        groups = groups_by_lang(call.message)
        keyboard = create_inline_kb(set(group.course_name for group in groups), chat_id, lang)
        bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id)
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=keyboard)

    else:
        text = 'отправить' if admin_selection[chat_id][0]['command'] == 'Отправить' else 'переслать'
        bot.delete_message(chat_id, message_id=call.message.message_id)
        bot.delete_message(chat_id, message_id=call.message.message_id+1)
        if 'All' in selected:
            bot.send_message(chat_id, f'Принял ваш запрос. Что вы хотите {text} во все группы')
        else:
            bot.send_message(chat_id,
                             f'Принял ваш запрос. Что вы хотите {text} в группу(ы) {", ".join(admin_selection[chat_id][2]["courses"])}')

        bot.register_next_step_handler(call.message, get_messages)

    bot.answer_callback_query(callback_query_id=call.id)


def course_select(message: types.Message, groups):
    group_filter_by_course = set(group.course_name for group in groups)
    keyboard = create_inline_kb(group_filter_by_course, message.chat.id, message.text)
    box_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    box_keyboard.add(types.KeyboardButton('Отменить'))
    bot.send_message(message.chat.id, 'Выберите курс', reply_markup=keyboard)
    bot.send_message(message.chat.id, 'Или отмените и начните заново', reply_markup=box_keyboard)


@bot.message_handler(is_admin=True, content_types=['text', 'audio', 'video', 'image', 'photo', 'voice', 'document'],
                     func=lambda message: True)
def get_messages(message: types.Message):
    cid = message.chat.id
    if message.text == 'Подтвердить':
        filter_groups(message)
    elif message.text == 'Отменить':
        del admin_selection[cid]
        admin_panel(message)
    else:

        msg_content = {}

        if message.text:
            msg_content = {'type': 'text', 'content': message.html_text, 'message_id': message.message_id}
        elif message.photo:
            msg_content = {'type': 'photo', 'file_id': message.photo[-1].file_id, 'caption': message.caption or '',
                           'message_id': message.message_id}
        elif message.audio:
            msg_content = {'type': 'audio', 'file_id': message.audio.file_id, 'caption': message.caption or '',
                           'message_id': message.message_id}
        elif message.video:
            msg_content = {'type': 'video', 'file_id': message.video.file_id, 'caption': message.caption or '',
                           'message_id': message.message_id}
        elif message.voice:
            msg_content = {'type': 'voice', 'file_id': message.voice.file_id, 'message_id': message.message_id}
        elif message.document:
            msg_content = {'type': 'document', 'file_id': message.document.file_id, 'caption': message.caption or '',
                           'message_id': message.message_id}

        admin_selection[cid][3]['messages'].append(msg_content)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton('Подтвердить'), types.KeyboardButton('Отменить'))
        bot.send_message(message.chat.id, 'Принял. Еще?', reply_markup=keyboard)
        print(admin_selection)
        bot.register_next_step_handler(message, get_messages)


def filter_groups(message: types.Message):
    cid = message.chat.id
    com, lang, crs, msgs = '', '', [], []
    if cid in admin_selection:
        com = admin_selection[cid][0]['command']
        lang = admin_selection[cid][1]['language']
        crs = admin_selection[cid][2]['courses']
        msgs = admin_selection[cid][3]['messages']
    else:
        bot.send_message(cid, 'Ошибка')

    # print(f'{com=}, {lang=}, {crs=}, {msgs=}')

    if lang != 'Все':
        print('here')
        groups = BotGroup.objects.filter(group_language=lang)
    else:
        groups = BotGroup.objects.all()

    filtered_groups = []
    if 'All' not in crs:
        for course in crs:
            temp_groups = groups.filter(course_name=course)
            for temp_group in temp_groups:
                filtered_groups.append(temp_group)
    else:
        temp_groups = groups.all()
        for temp_group in temp_groups:
            filtered_groups.append(temp_group)
    if com == 'Отправить':
        for group in filtered_groups:
            media_group = []

            for msg in msgs:
                if msg['type'] in ['photo', 'video']:
                    media_item = (
                        InputMediaPhoto(msg['file_id'], caption=msg['caption'])
                        if msg['type'] == 'photo'
                        else InputMediaVideo(msg['file_id'], caption=msg['caption'])
                    )
                    media_group.append(media_item)

                    if len(media_group) == 10:
                        bot.send_media_group(group.chat_id, media_group)
                        media_group = []

                else:
                    if media_group:
                        bot.send_media_group(group.chat_id, media_group)
                        media_group = []

                    if msg['type'] == 'text':
                        bot.send_message(group.chat_id, msg['content'], parse_mode='html')
                    elif msg['type'] == 'audio':
                        bot.send_audio(group.chat_id, msg['file_id'], caption=msg['caption'])
                    elif msg['type'] == 'voice':
                        bot.send_voice(group.chat_id, msg['file_id'])
                    elif msg['type'] == 'document':
                        bot.send_document(group.chat_id, msg['file_id'], caption=msg['caption'], parse_mode='html')

            if media_group:
                bot.send_media_group(group.chat_id, media_group)
    else:
        for group in filtered_groups:
            for msg in msgs:
                if msg['type'] in ['photo', 'video']:
                    bot.forward_message(group.chat_id, cid, msg['message_id'])

            for msg in msgs:
                if msg['type'] not in ['photo', 'video']:
                    bot.forward_message(group.chat_id, cid, msg['message_id'])

    bot.send_message(cid, 'Готово')
    if cid in admin_selection:
        del admin_selection[cid]
    admin_panel(message)
