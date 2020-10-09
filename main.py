from viberbot.api.viber_requests import ViberUnsubscribedRequest

from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.viber_requests import ViberFailedRequest, ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest

import random
import time
import logging
import sched
import threading
import pymysql

PAYMENT = dict()
PAYMENT['transaction_id'] = 0
PAYMENT['transaction_type'] = 'defrayal'
PAYMENT['transaction_amount'] = 0
# Словарь сессии
SESSION = dict()
SESSION['is_auth'] = False
SESSION['client_id'] = '000000000'
SESSION['client_contract'] = '00/00/00'
SESSION['client_debt'] = 0
SESSION['client_tariff'] = 0
SESSION['client_recommended_payment'] = SESSION['client_debt'] + SESSION['client_tariff']
SESSION['client_for_year_payment'] = SESSION['client_tariff'] * 0.9

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

keyboard = \
    {
        "DefaultHeight": True,
        "BgColor": "#000000",
        "Type": "keyboard",
        "Buttons": [
            {
                "Columns": 6,
                "Rows": 1,
                "Text": "<font color=\"#ffffff\">Увійти</font>",
                "BgColor": "#262626",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": "Увійти",
                "ReplyType": "message"
            }
        ]
    }

smm_keyboard = \
    {
        "DefaultHeight": True,
        "BgColor": "#000000",
        "Type": "keyboard",
        "Buttons": [
            {
                "Columns": 3,
                "Rows": 1,
                "Text": "<font color=\"#ffffff\">Стан рахунку</font>",
                "BgColor": "#262626",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": "Стан рахунку",
                "ReplyType": "message"
            },
            {
                "Columns": 3,
                "Rows": 1,
                "Text": "<font color=\"#ffffff\">Перейти до оплати</font>",
                "BgColor": "#262626",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": "Перейти до оплати",
                "ReplyType": "message"
            },
            {
                "Columns": 3,
                "Rows": 1,
                "Text": "<font color=\"#ffffff\">Інформація по рахунку</font>",
                "BgColor": "#262626",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": "Інформація по рахунку",
                "ReplyType": "message"
            },
            {
                "Columns": 3,
                "Rows": 1,
                "Text": "<font color=\"#ffffff\">Наші реквізити</font>",
                "BgColor": "#262626",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": "Наші реквізити",
                "ReplyType": "message"
            },
            {
                "Columns": 6,
                "Rows": 1,
                "Text": "<font color=\"#ffffff\">Фінансова історія</font>",
                "BgColor": "#262626",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": "Фінансова історія",
                "ReplyType": "message"
            },
            {
                "Columns": 3,
                "Rows": 1,
                "Text": "<font color=\"#ffffff\">Контакти</font>",
                "BgColor": "#262626",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": "Контакти",
                "ReplyType": "message"
            },
            {
                "Columns": 3,
                "Rows": 1,
                "Text": "<font color=\"#ffffff\">Графік роботи</font>",
                "BgColor": "#262626",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": "Графік роботи",
                "ReplyType": "message"
            },
            {
                "Columns": 3,
                "Rows": 1,
                "Text": "<font color=\"#ffffff\">Вийти...</font>",
                "BgColor": "#262626",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": "Вийти...",
                "ReplyType": "message"
            },
            {
                "Columns": 3,
                "Rows": 1,
                "Text": "<font color=\"#ffffff\">Увійти</font>",
                "BgColor": "#262626",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": "Увійти",
                "ReplyType": "message"
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
    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        global temp_password
        global temp_chat_id
        message = viber_request.message

        if message.text == 'Увійти':
            viber.send_messages(viber_request.sender.id, [TextMessage(text='Введіть, будь ласка, свій особовий рахунок')])

        elif len(message.text) == 9:
            def password_saving(client_id):
                viber.send_messages(viber_request.sender.id,
                                    [TextMessage(text='Введіть, будь ласка, свій пароль')])
                link = pymysql.connect('prime00.mysql.tools', 'prime00_clients', '8y&@40oInG', 'prime00_clients')
                cursor = link.cursor()
                password_query = """SELECT user_password FROM users WHERE user_id='""" + client_id + """'"""
                cursor.execute(password_query)
                password = cursor.fetchone()
                link.commit()
                return password

            SESSION['client_id'] = message.text
            temp_password = password_saving(message.text)
        elif len(message.text) == 5:
            str_correct_password = str(temp_password)
            maybe_password = "('" + message.text + "',)"
            if str_correct_password == maybe_password:
                temp_chat_id = viber_request.sender.id
                viber.send_messages(viber_request.sender.id, [TextMessage(text='Вітаємо в персональному кабінеті! Ви успішно залоговані.',
                                                 keyboard=smm_keyboard)])

                def client_contract_extracting(client_id):
                    link = pymysql.connect('prime00.mysql.tools', 'prime00_clients', '8y&@40oInG', 'prime00_clients')
                    cursor = link.cursor()
                    client_contract_query = """SELECT user_contract_num FROM users WHERE user_id='""" + client_id + """'"""
                    cursor.execute(client_contract_query)
                    contract = cursor.fetchone()
                    return contract

                def client_tariff_extracting(client_id):
                    link = pymysql.connect('prime00.mysql.tools', 'prime00_clients', '8y&@40oInG', 'prime00_clients')
                    cur = link.cursor()
                    client_contract_query = """SELECT user_tax FROM users WHERE user_id='""" + client_id + """'"""
                    cur.execute(client_contract_query)
                    tariff = cur.fetchone()
                    return tariff[0]

                def client_debt_extracting(client_id):
                    link = pymysql.connect('prime00.mysql.tools', 'prime00_clients', '8y&@40oInG', 'prime00_clients')
                    cur = link.cursor()
                    client_rev_query = """SELECT SUM(transaction_sum) FROM payment_story WHERE transaction_client='""" + client_id + """'"""
                    cur.execute(client_rev_query)
                    rev = cur.fetchone()
                    client_debt_at_the_start_query = """SELECT user_balance FROM users WHERE user_id='""" + client_id + """'"""
                    cur.execute(client_debt_at_the_start_query)
                    debt_at_the_start = cur.fetchone()
                    if rev[0]:
                        result_sum = debt_at_the_start[0] + rev[0]
                    else:
                        result_sum = debt_at_the_start[0] + 0
                    return result_sum

                SESSION['is_auth'] = True
                SESSION['client_contract'] = client_contract_extracting(SESSION['client_id'])
                SESSION['client_tariff'] = client_tariff_extracting(SESSION['client_id'])
                SESSION['client_debt'] = client_debt_extracting(SESSION['client_id'])
                SESSION['client_recommended_payment'] = SESSION['client_debt'] + SESSION['client_tariff']
                SESSION['client_for_year_payment'] = float(SESSION['client_tariff']) * 12 * 0.9
                viber.send_messages(viber_request.sender.id, [TextMessage(text='В меню ви можете знайти доступні операції та здійснити оплату',
                                                 keyboard=smm_keyboard)])

            elif str_correct_password != maybe_password:
                viber.send_messages(viber_request.sender.id, [TextMessage(text='Введені дані некоректні! Перевірте пароль та спробуйте ще раз.', keyboard=keyboard)])

        elif message.text == 'Вийти...' and SESSION['is_auth']:
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text='Ви успішно вийшли з персонального кабінету!', keyboard=keyboard)])

            SESSION['is_auth'] = False
            SESSION['client_id'] = None
            SESSION['client_contract'] = None
            SESSION['client_debt'] = None
            SESSION['client_tariff'] = None
            SESSION['client_recommended_payment'] = None
            SESSION['client_for_year_payment'] = None

        elif message.text == 'Стан рахунку' and SESSION['is_auth']:
            if SESSION['client_debt'] > 0:
                viber.send_messages(viber_request.sender.id, [TextMessage(text="""Ваша заборгованість: """ + str(
                    SESSION['client_debt']) + """ гривень. Будь ласка, сплатіть її до 10 числа поточного місяця.""", keyboard=smm_keyboard)])
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(text='Рекомендований платіж: ' + str(SESSION['client_recommended_payment']) + ' гривень', keyboard=smm_keyboard)])
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(text='Разовий платіж за рік: ' + str(SESSION['client_for_year_payment']) + ' гривень',
                        keyboard=smm_keyboard)])
            else:
                viber.send_messages(viber_request.sender.id, [TextMessage(
                    text='Шановний клієнте, у вас відсутня заборгованість! ' + 'Ваш авансовий платіж: ' + str(
                        SESSION['client_debt']) + ' гривень. Дякуємо, що вчасно сплачуєте рахунки!', keyboard=smm_keyboard)])
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(text='Разовий платіж за рік: ' + str(SESSION['client_for_year_payment']) + ' гривень',
                        keyboard=smm_keyboard)])

        elif message.text == 'Інформація по рахунку' and SESSION['is_auth']:
            viber.send_messages(viber_request.sender.id,
                                [TextMessage(text='Ваш особовий рахунок: ' + str(SESSION['client_id']), keyboard=smm_keyboard)])
            viber.send_messages(viber_request.sender.id, [TextMessage(
                text='Ваш номер договору: ' + str(SESSION['client_contract']).replace('(', '').replace("'", '').replace(
                    ',',
                    '').replace(
                    ')', ''), keyboard=smm_keyboard)])
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text='Сума щомісячного платежу: ' + str(SESSION['client_tariff']) + ' гривень',
                            keyboard=smm_keyboard)])

        elif message.text == 'Наші реквізити' and SESSION['is_auth']:
            viber.send_messages(viber_request.sender.id, [TextMessage(text=
'''ТОВ "ПРАЙМ-СЕКЬЮРІТІ".
Код за ЄДРПОУ 38958975,
п/р UA983510050000026006564312000,
у банку АТ  "УкрСиббанк"
Київ, МФО 351005, Київська обл.,Києво-Святошинський р., с.Петропавлівська Борщагівка,вул.Миру,буд.11,прим.150, 08130,
тел.: (066) 5979518''', keyboard=smm_keyboard)])

        elif message.text == 'Фінансова історія' and SESSION['is_auth']:
            def payment_extracting(client_id):
                link = pymysql.connect('prime00.mysql.tools', 'prime00_clients', '8y&@40oInG', 'prime00_clients')
                cur = link.cursor()
                query_4_countcheck = "SELECT transaction_id FROM payment_story WHERE transaction_client='" + client_id + "'ORDER BY transaction_id DESC LIMIT 10"
                cur.execute(query_4_countcheck)
                countcheck = cur.fetchall()
                cur = link.cursor()
                query_id = "SELECT transaction_id FROM payment_story WHERE transaction_client='" + client_id + "' ORDER BY transaction_id DESC"
                cur.execute(query_id)
                payment_ids = cur.fetchall()
                query_datetime = "SELECT transaction_datetime FROM payment_story WHERE transaction_client='" + client_id + "'ORDER BY transaction_id DESC"
                cur.execute(query_datetime)
                payment_datetimes = cur.fetchall()
                query_type = "SELECT transaction_type FROM payment_story WHERE transaction_client='" + client_id + "'ORDER BY transaction_id DESC"
                cur.execute(query_type)
                payment_types = cur.fetchall()
                query_sum = "SELECT transaction_sum FROM payment_story WHERE transaction_client='" + client_id + "'ORDER BY transaction_id DESC"
                cur.execute(query_sum)
                payment_sums = cur.fetchall()
                i = 0
                while i < len(countcheck):
                    viber.send_messages(viber_request.sender.id, [TextMessage(
                        text='id: ' + str(payment_ids[i]).replace('(', '').replace(',', '').replace(')', '') + ''', 
            дата: ''' + str(payment_datetimes[i]).replace('(', '').replace(',', '').replace(')', '').replace('d',
                                                                                                             '').replace(
                                'a', '').replace('t', '').replace('e', '').replace('i', '').replace('m', '').replace(
                                '.', '').replace(' ', '-').replace('-0-0', '') + ''',
            тип транзакції: ''' + str(payment_types[i]).replace('(', '').replace(',', '').replace(')', '').replace("'",
                                                                                                                   '').replace(
                                'nachislenie', 'нарахування').replace('oplata schota', 'оплата') + ''', 
            сума: ''' + str(payment_sums[i]).replace('D', '').replace('e', '').replace('c', '').replace('i',
                                                                                                        '').replace('m',
                                                                                                                    '').replace(
                                'a', '').replace('l', '').replace('(', '').replace("'", '').replace(')', '').replace(
                                ',', '') + ' гривень', keyboard=smm_keyboard)])
                    i = i + 1
            viber.send_messages(viber_request.sender.id, [TextMessage(text='Останні транзакції:', keyboard=smm_keyboard)])
            payment_extracting(SESSION['client_id'])

        elif message.text == 'Контакти' and SESSION['is_auth']:
            viber.send_messages(viber_request.sender.id, [TextMessage(text='Бухгалтерія: 066-597-95-18', keyboard=smm_keyboard)])
            viber.send_messages(viber_request.sender.id, [TextMessage(text='Гаряча лінія: 067-323-80-08', keyboard=smm_keyboard)])
            viber.send_messages(viber_request.sender.id, [TextMessage(text='admin@prime.net.ua', keyboard=smm_keyboard)])
            viber.send_messages(viber_request.sender.id, [TextMessage(text='Наш сайт: https://www.prime.net.ua/', keyboard=smm_keyboard)])
            viber.send_messages(viber_request.sender.id, [TextMessage(text='с. Петропавлівська Борщагівка ЖК «Львівський», вул. Миру 11', keyboard=smm_keyboard)])

        elif message.text == 'Графік роботи' and SESSION['is_auth']:
            viber.send_messages(viber_request.sender.id, [TextMessage(text='''Понеділок: 09:00-18:00
Вівторок: 09:00-18:00
Середа: 09:00-18:00
Четвер: 09:00-18:00
П'ятниця: 09:00-18:00
Субота: вихідний
Неділя: вихідний
13:00-14:00 - обід''', keyboard=smm_keyboard)])

        elif message.text == 'Перейти до оплати' and SESSION['is_auth']:
            viber.send_messages(viber_request.sender.id, [TextMessage(text='Портмоне: portmone.com.ua/r3/oplata-ohrany-prime-security-kievskaya-oblast', keyboard=smm_keyboard)])

    elif isinstance(viber_request, ViberConversationStartedRequest):
        viber.send_messages(viber_request.user.id, [TextMessage(text="Вітаємо! Натисніть на кнопку для того, щоб увійти в персональний кабінет клієнта.", keyboard=keyboard)])

    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request), keyboard=keyboard)

    return Response(status=200)


def set_webhook(vib):
    viber.set_webhook('https://d46cedebdd3d.ngrok.io')


if __name__ == "__main__":
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(5, 1, set_webhook, (viber,))
    t = threading.Thread(target=scheduler.run)
    t.start()

    context = ('server.crt', 'server.key')
    app.run(host='0.0.0.0', port=8443, debug=True)
