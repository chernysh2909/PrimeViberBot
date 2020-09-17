from viberbot.api.viber_requests import ViberUnsubscribedRequest

from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.viber_requests import ViberFailedRequest, ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest

import xml.etree.ElementTree
import random
import time
import logging
import sched
import threading
import pymysql

link = pymysql.connect('prime00.mysql.tools', 'prime00_clients', '8y&@40oInG', 'prime00_clients')

operators = []
operator = {'chat_id': None, 'name': None, 'work': None}

smm = []

password = None

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

keyboard =\
            {
            "DefaultHeight": True,
            "BgColor": "#FFFFFF",
            "Type": "keyboard",
            "Buttons": [
                {
                    "Columns": 6,
                    "Rows": 1,
                    "BgColor": "#e6f5ff",
                    "BgLoop": True,
                    "ActionType": "reply",
                    "ActionBody": "Увійти",
                    "ReplyType": "message",
                    "Text": "Увійти"
                },
                {
                    "Columns": 6,
                    "Rows": 1,
                    "BgColor": "#e6f5ff",
                    "BgLoop": True,
                    "ActionType": "reply",
                    "ActionBody": "Стати клієнтом",
                    "ReplyType": "message",
                    "Text": "Стати клієнтом"
                }
            ]
            }

app = Flask(__name__)

viber = Api(BotConfiguration(
  name='PrimeSecurityBot',
  avatar='http://site.com/avatar.jpg',
  auth_token='4c26c6fd10e7d327-52ad10fcdb87074c-b9c8a79085b4a1f9'
))

@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))
    viber_request = viber.parse_request(request.get_data().decode('utf8'))

    if isinstance(viber_request, ViberConversationStartedRequest):
        viber.send_messages(viber_request.get_user().get_id(), [
            TextMessage(text="Оберіть одну з кнопок нижче.")
        ])


    return Response(status=200)

def set_webhook(vib):
    viber.set_webhook('')

    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=8443, debug=True)


