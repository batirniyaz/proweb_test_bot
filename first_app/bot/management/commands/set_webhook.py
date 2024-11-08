from django.core.management.base import BaseCommand

from ...bot_instance import bot
from ...credentials import WEBHOOK_URL


class Command(BaseCommand):
    help = 'set webhook of telegram bot'

    def handle(self, *args, **kwargs):
        bot.set_webhook(
            WEBHOOK_URL,
            allowed_updates=['my_chat_member']
        )
        print('webhook set successfully')
