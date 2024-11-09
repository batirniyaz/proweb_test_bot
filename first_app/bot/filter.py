import telebot

from .models import BotUser


class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    key = 'is_admin'

    @staticmethod
    def check(message: telebot.types.Message):
        try:
            user = BotUser.objects.get(chat_id=message.chat.id)
        except BotUser.DoesNotExist:
            return False
        return True if user.role == 'admin' else False