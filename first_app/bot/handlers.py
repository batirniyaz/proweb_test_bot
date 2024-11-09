import time
from threading import Timer

from telebot import types

from .handlers_admin import admin_panel
from .messages import messages, messages_uz

from .credentials import FEEDBACK_GROUP_ID, BOT_ID
from .bot_instance import bot
from .models import BotUser, BotGroup

user_time = {}


def get_name(message):
    first_name = f'{message.from_user.first_name}'
    last_name = f'{message.from_user.last_name if message.from_user.last_name else None}'
    username = f'{message.from_user.username if message.from_user.username else None}'
    return {'firstname': first_name, 'lastname': last_name or '', 'username': username or ''}


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


def welcome_buttons_uz():
    markup = types.InlineKeyboardMarkup()
    support_btn = types.InlineKeyboardButton('Texnik yordam', url='t.me/itsmylifestyle')
    coworking_btn = types.InlineKeyboardButton('Kovorking', url='t.me/proweb_coworking')
    concurs_btn = types.InlineKeyboardButton('Tanlovlar 🎉', callback_data='conkurs')
    webpage_btn = types.InlineKeyboardButton('Saytga tashrif buyurish', url='https://www.proweb.uz')
    basic_btn = types.InlineKeyboardButton('Kompyuter asoslari', callback_data='basic_course')
    review_btn = types.InlineKeyboardButton('Sharh qoldirish', callback_data='review')

    markup.row(support_btn, coworking_btn)
    markup.row(concurs_btn, webpage_btn)
    markup.row(basic_btn, review_btn)
    markup.add(types.InlineKeyboardButton('Oqish qoydalari', callback_data='licence'))

    box_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = types.KeyboardButton('Bosh sahifaga')
    lang_btn = types.KeyboardButton("Русcкий язык 🇷🇺")
    box_markup.row(back_btn, lang_btn)

    return markup, box_markup


@bot.message_handler(commands=['start'], chat_types=['private'], is_admin=False)
def send_welcome(message: types.Message):
    chat_id = message.chat.id
    full_name = get_name(message)

    user = BotUser.objects.filter(chat_id=chat_id).first()

    if not user:
        BotUser.objects.create(
            chat_id=chat_id,
            username=full_name['username'],
            first_name=full_name['firstname'],
            last_name=full_name['lastname'],
        )
        user = BotUser.objects.get(chat_id=chat_id)

    if user.language == 'ru':
        markup, box_markup = welcome_buttons()
        bot.send_message(message.chat.id, messages.welcome_message, parse_mode='html', reply_markup=box_markup)
        bot.send_message(message.chat.id, messages.help_message, parse_mode='html', reply_markup=markup)
    else:
        markup, box_markup = welcome_buttons_uz()
        bot.send_message(message.chat.id, messages_uz.welcome_message, parse_mode='html', reply_markup=box_markup)
        bot.send_message(message.chat.id, messages_uz.help_message, parse_mode='html', reply_markup=markup)

    bot.register_next_step_handler(message, on_click)


@bot.message_handler(commands=['help'], chat_types=['private'])
def send_help(message):
    bot.send_message(message.chat.id, messages.help_message, parse_mode='html')


@bot.message_handler(commands=['getchatid'])
def getchatid(message: types.Message):
    cid = message.chat.id
    mid = message.message_id
    fid = message.from_user.id
    bot.send_message(message.chat.id, '\n'.join([f'cid: {cid}', f'mid: {mid}', f'fid: {fid}']))


@bot.message_handler(func=lambda message: True, chat_types=['private'])
def on_click(message):
    markup, box_markup = welcome_buttons()
    markup_uz, box_markup_uz = welcome_buttons_uz()
    user = BotUser.objects.get(chat_id=message.chat.id)

    if message.text == 'На главную':
        bot.send_message(message.chat.id, messages.help_message, parse_mode='html', reply_markup=markup)
    elif message.text == 'Bosh sahifaga':
        bot.send_message(message.chat.id, messages_uz.help_message, parse_mode='html', reply_markup=markup_uz)
    elif message.text == "O'zbek tili 🇺🇿":
        user.language = 'uz'
        user.save()
        bot.send_message(message.chat.id, "Til o'zbekchaga ogirildi", reply_markup=box_markup_uz)
        bot.send_message(message.chat.id, messages_uz.help_message, parse_mode='html', reply_markup=markup_uz)
    elif message.text == "Русcкий язык 🇷🇺":
        user.language = 'ru'
        user.save()
        bot.send_message(message.chat.id, "Язык изменен на русский", reply_markup=box_markup)
        bot.send_message(message.chat.id, messages.help_message, parse_mode='html', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data == 'conkurs')
def call_concurs(callback: types.CallbackQuery):
    user = BotUser.objects.get(chat_id=callback.from_user.id)
    if user.language == 'ru':
        bot.send_message(callback.message.chat.id, messages.conkurs_message, parse_mode='html')
    else:
        bot.send_message(callback.message.chat.id, messages_uz.conkurs_message, parse_mode='html')

    bot.answer_callback_query(callback_query_id=callback.id)


@bot.callback_query_handler(func=lambda callback: callback.data == 'basic_course')
def call_basic_course(callback: types.CallbackQuery):
    user = BotUser.objects.get(chat_id=callback.from_user.id)

    basic_course_markup = types.InlineKeyboardMarkup()
    if user.language == 'ru':
        bsc_btn = types.InlineKeyboardButton('Записаться на базовый курс', url='t.me/proweb_basics')
        basic_course_markup.add(bsc_btn)

        bot.send_message(callback.message.chat.id, messages.basic_course_message, parse_mode='html',
                         reply_markup=basic_course_markup)
    else:
        bsc_btn = types.InlineKeyboardButton('Kompyuter asoslari kursiga yozilish', url='t.me/proweb_basics')
        basic_course_markup.add(bsc_btn)

        bot.send_message(callback.message.chat.id, messages_uz.basic_course_message, parse_mode='html',
                         reply_markup=basic_course_markup)

    bot.answer_callback_query(callback_query_id=callback.id)


@bot.callback_query_handler(func=lambda callback: callback.data == 'review')
def call_review(callback: types.CallbackQuery):
    user = BotUser.objects.get(chat_id=callback.from_user.id)

    review_markup = types.InlineKeyboardMarkup()
    if user.language == 'ru':
        rvw_btn = types.InlineKeyboardButton('Отзывы 😍', url='https://proweb.uz/reviews/')
        cmp_sggtn_btn = types.InlineKeyboardButton('Жалобы и пожелания 😔', callback_data='complains_and_suggestions')
        review_markup.row(rvw_btn, cmp_sggtn_btn)

        bot.send_message(callback.message.chat.id, messages.review_message, parse_mode='html',
                         reply_markup=review_markup)
    else:
        rvw_btn = types.InlineKeyboardButton('Sharhlar 😍', url='https://proweb.uz/reviews/')
        cmp_sggtn_btn = types.InlineKeyboardButton('Shikoyat va istaklar 😔', callback_data='complains_and_suggestions')
        review_markup.row(rvw_btn, cmp_sggtn_btn)
        bot.send_message(callback.message.chat.id, messages_uz.review_message, parse_mode='html',
                         reply_markup=review_markup)

    bot.answer_callback_query(callback_query_id=callback.id)


@bot.callback_query_handler(func=lambda callback: callback.data == 'licence')
def call_licence(callback: types.CallbackQuery):
    user = BotUser.objects.get(chat_id=callback.from_user.id)
    if user.language == 'ru':
        bot.send_message(callback.message.chat.id, messages.licence_message, parse_mode='html',
                         disable_web_page_preview=True)
    else:
        bot.send_message(callback.message.chat.id, messages_uz.licence_message, parse_mode='html',
                         disable_web_page_preview=True)

    bot.answer_callback_query(callback_query_id=callback.id)


@bot.callback_query_handler(func=lambda callback: callback.data == 'complains_and_suggestions')
def call_complains_and_suggestions(callback: types.CallbackQuery):
    user = BotUser.objects.get(chat_id=callback.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user.language == 'ru':
        contact_btn = types.KeyboardButton('Поделиться контактом', request_contact=True)
        keyboard.add(contact_btn)

        bot.send_message(callback.message.chat.id, messages.complain_suggestion_message, parse_mode='html',
                         reply_markup=keyboard)
    else:
        contact_btn = types.KeyboardButton('Kontakt bilan ulashing', request_contact=True)
        keyboard.add(contact_btn)

        bot.send_message(callback.message.chat.id, messages_uz.complain_suggestion_message, parse_mode='html',
                         reply_markup=keyboard)

    bot.answer_callback_query(callback_query_id=callback.id)
    bot.register_next_step_handler(callback.message, send_contact)


@bot.message_handler(content_types=['contact'], chat_types=['private'])
def send_contact(message):
    user = BotUser.objects.get(chat_id=message.from_user.id)

    if message.from_user.id == message.contact.user_id:
        user_phone_number = message.contact.phone_number
        user_time[message.chat.id] = {'time': time.time()}
        print(time.time())

        if user.language == 'ru':
            bot.send_message(message.chat.id, 'Теперь, напишите чтобы вы хотели предложить или на что жалуетесь?')
        else:
            bot.send_message(message.chat.id,
                             'Endi nima taklif qilmoqchisiz yoki nimadan shikoyat qilayotganingizni yozing?')

        timer = Timer(1800, complain_text, args=[message, user_phone_number, 'Netu'])
        user_time[message.chat.id]['timer'] = timer
        timer.start()

        bot.register_next_step_handler(message, send_complain_text, user_phone_number)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста отправьте <b>СВОЙ</b> номер телефона', parse_mode='html')


def complain_text(message, user_phone, text=None):
    user = BotUser.objects.get(chat_id=message.chat.id)

    bot.send_message(FEEDBACK_GROUP_ID, f'User id: {message.from_user.id}\n'
                                        f'User: @{message.from_user.username if message.from_user.username else "Нету"}\n'
                                        f'Name: {message.from_user.first_name}\n'
                                        f'Phone: {user_phone}\n'
                                        f'Message: {message.text if not text else text}')

    markup, box_markup = welcome_buttons()
    markup_uz, box_markup_uz = welcome_buttons_uz()

    if user.language == 'ru':
        bot.send_message(message.from_user.id,
                         f"Спасибо за обращение!, {messages.text if message.content_type == 'text' else messages.phone}",
                         reply_markup=box_markup)
        bot.send_message(message.from_user.id, messages.help_message, parse_mode='html', reply_markup=markup)
    else:
        bot.send_message(message.from_user.id,
                         f"Murojaat qilganingiz uchun tashakkur!, {messages_uz.text if message.content_type == 'text' else messages_uz.phone}",
                         reply_markup=box_markup_uz)
        bot.send_message(message.from_user.id, messages_uz.help_message, parse_mode='html', reply_markup=markup_uz)


@bot.message_handler(content_types=['text'], func=lambda message: True, chat_types=['private'])
def send_complain_text(message, user_phone):

    if message.chat.id in user_time:
        timer = user_time[message.chat.id].get('timer')
        if timer:
            timer.cancel()

        del user_time[message.chat.id]

        complain_text(message, user_phone)


@bot.my_chat_member_handler()
def get_new_group(message: types.ChatMemberUpdated):
    chat_id = message.chat.id
    chat_name = message.chat.title

    if message.new_chat_member.status == 'member':
        if type(chat_name) == str and chat_name.startswith('PROWEB.'):
            chat_name = chat_name[7:]
            try:
                course_name, language, graphic, group_time = chat_name.split(' ', 4)
                if language not in ('УЗБ', 'РУС'):
                    raise ValueError("Неверный язык. Должно быть «УЗБ» или «РУС».")
                if '-' not in graphic or not graphic.replace('-', '').isalpha():
                    raise ValueError("Недопустимая графика. Пример: «ПН-ЧТ».")
                if not group_time.replace(':', '').isdigit():
                    raise ValueError("Неверное время. Пример: «17:00».")

                group, created = BotGroup.objects.update_or_create(
                    chat_id=chat_id,
                    defaults={
                        'chat_name': chat_name,
                        'course_name': course_name,
                        'group_language': language,
                        'group_graphic': graphic,
                        'group_time': group_time,
                    }
                )

                bot.send_message(chat_id, f"Группа {'добавлен' if created else 'обновлено'}: {chat_name}")
                bot.send_message(message.from_user.id, f'Бот успешно добавил группу {chat_name} в БД')
            except ValueError as e:
                bot.send_message(chat_id, f"Ошибка в структуре названия группы: {str(e)}")

    if message.new_chat_member.status == 'left':
        chat_id = message.chat.id

        try:
            group = BotGroup.objects.get(chat_id=chat_id)
        except BotGroup.DoesNotExist:
            return 'not match'
        if group:
            group.delete()
            print("Delete")
            bot.send_message(message.from_user.id,
                             f'Бот был исключен из группы: {chat_name}. И я удалил его id {chat_id} из БД')
        else:
            print("no bot")
