import json

import telebot
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST

from .credentials import TOKEN

from .bot_instance import bot

from . import handlers


API_TOKEN = TOKEN


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









# @bot.callback_query_handler(func=lambda callback: True)



# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     bot.reply_to(message, message.text)
