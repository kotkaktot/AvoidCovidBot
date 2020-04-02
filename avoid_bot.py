import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from settings import token, yandex_token, parse_content, radius
from decimal import Decimal
from yandex_geocoder import Client
import requests
import re
import json
import geopy.distance

updater = Updater(token, use_context=True)
ya_client = Client(yandex_token)


def get_addresses():
    # dictionary for collecting covid location points
    points_dic = {}

    url = 'https://mash.ru/letter/coronavirus-2/'
    html = requests.get(url)

    dirt_adr = re.findall('(hintContent: ".+)', html.text)
    dirt_coords = re.findall('(ymaps.Placemark\(\[\d+.\d+,\d+.\d+\])', html.text)

    for i in range(len(dirt_coords)):
        # print(dirt_adr[i])
        coords_list = dirt_coords[i].split('[')[1][:-1].split(',')

        # print(coords_list[0], coords_list[1])

        # request to ya_api
        ya_addr_clear = ya_client.address(Decimal(coords_list[1]), Decimal(coords_list[0]))
        # print(ya_addr_clear)
        # print('-' * 10)
        points_dic[ya_addr_clear] = coords_list
        print(i)

    # writing dic to json file
    with open('points.txt', 'w', encoding='utf8') as outfile:
        json.dump(points_dic, outfile, ensure_ascii=False)


def read_points_json():
    with open('points.txt', encoding='utf8') as json_file:
        return json.load(json_file)


def geo(update, context):
    coords = update.message.location
    lat = coords['latitude']
    long = coords['longitude']
    dic = find_near_points(lat, long)
    # print(dic)

    if len(dic) > 0:
        msg_text = '*Береги себя друг, по моим данным в радиусе {} км. зафиксированы случаи COVID-19:*\n\n'\
            .format(radius, len(dic))
        for key in dic:
            msg_text += '{}\n\n'.format(str(key))
    else:
        msg_text = '*Поздравляю друг, по моим данным в радиусе {} км. случаев COVID-19 не зафиксировано!*'.format(radius)

    # print(msg_text)
    update.message.reply_text(text=msg_text, parse_mode=telegram.ParseMode.MARKDOWN)


def find_near_points(lat, long):
    dic = read_points_json()
    # print(dic)
    near_points = []
    for key in dic:
        # print(key, dic[key])
        dist = geopy.distance.distance(tuple(dic[key]), (lat, long)).km
        # print(dist)
        if dist <= radius:
            near_points.append('{} км. - {}'.format(round(dist, 2), key))
    return near_points


# parsing actual covid points from Mash
if parse_content:
    get_addresses()

geo_handler = MessageHandler(Filters.location, geo)
updater.dispatcher.add_handler(geo_handler)
updater.start_polling()
updater.idle()
