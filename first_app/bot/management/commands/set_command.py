import telebot.types
from django.core.management.base import BaseCommand

from ...bot_instance import bot


class Command(BaseCommand):
    help = 'set commands of telegram bot'

    def handle(self, *args, **kwargs):

        bot.set_my_commands(
            commands=[
                telebot.types.BotCommand('start', 'start the bot'),
                telebot.types.BotCommand('help', 'extend information about bot'),
                telebot.types.BotCommand('getchatid', 'to get id of this chat'),
            ],
            scope=telebot.types.BotCommandScopeAllPrivateChats()
        )
        print('commands set successfully')
        cmd = bot.get_my_commands(scope=None, language_code=None)
        print([c.to_json() for c in cmd])
