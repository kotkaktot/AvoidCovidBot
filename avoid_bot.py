from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from settings import token, yandex_token, parse_content
from decimal import Decimal
from yandex_geocoder import Client
import requests
import re

updater = Updater(token, use_context=True)
ya_client = Client(yandex_token)


def get_addresses():
    url = 'https://mash.ru/letter/coronavirus-2/'
    html = requests.get(url)

    dirt_adr = re.findall('(hintContent: ".+)', html.text)
    dirt_coords = re.findall('(ymaps.Placemark\(\[\d+.\d+,\d+.\d+\])', html.text)

    for i in range(len(dirt_adr)):
        print(dirt_adr[i])
        coords_list = dirt_coords[i].split('[')[1][:-1].split(',')

        print(coords_list[0], coords_list[1])

        # test request to ya_api
        print(ya_client.address(Decimal(coords_list[1]), Decimal(coords_list[0])))
        print('-' * 10)


def geo(update, context):
    print(update.message.location)


# парсим актуальные данные с Mash и получаем красивые адреса через Яндекс.Геокодер
if parse_content:
    get_addresses()

geo_handler = MessageHandler(Filters.location, geo)
updater.dispatcher.add_handler(geo_handler)
updater.start_polling()
updater.idle()
