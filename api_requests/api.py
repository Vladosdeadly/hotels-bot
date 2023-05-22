from datetime import datetime
from typing import Dict
from telebot import types
import requests
from loader import bot
from keyboards.commands_markup import city_choice
from database.history_classes import User, Hotel
from loguru import logger
from loader import API_KEY


class API:
    """
    Класс, в котором содержится вся основная информация для запросов к API сайта hotels.com.
    """
    min_date = datetime.now()
    url1 = "https://hotels4.p.rapidapi.com/locations/v3/search"
    url2 = "https://hotels4.p.rapidapi.com/properties/v2/list"
    url3 = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    headers1 = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": ""},
        "checkInDate": {
            "day": 0,
            "month": 0,
            "year": 0
        },
        "checkOutDate": {
            "day": 0,
            "month": 0,
            "year": 0
        },
        "rooms": [
            {
                "adults": 0
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 0,
        "sort": "PRICE_LOW_TO_HIGH",
        "filters": {"price": {
            "max": 200,
            "min": 10
        }}
    }
    headers2 = {
        "content-type": "application/json",
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    payload_detail = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": ''
    }


def enter_api_parametres(first_dict: Dict, second_dict: Dict):
    """
    Заполняет форму для запроса к API из введенных пользователем данных.

    :param first_dict: dict
    :param second_dict: dict
    :return: None
    """
    first_dict['destination']['regionId'] = second_dict['regionId']
    first_dict['checkInDate']['day'] = int(second_dict['date_in']['d'])
    first_dict['checkInDate']['month'] = int(second_dict['date_in']['m'])
    first_dict['checkInDate']['year'] = int(second_dict['date_in']['y'])
    first_dict['checkOutDate']['day'] = int(second_dict['date_out']['d'])
    first_dict['checkOutDate']['month'] = int(second_dict['date_out']['m'])
    first_dict['checkOutDate']['year'] = int(second_dict['date_out']['y'])
    first_dict['rooms'][0]['adults'] = int(second_dict['people_count'])


@logger.catch()
def get_city(message: types.Message, word) -> None:
    """
    Делает запрос к API, передавая город, введенный пользователем.
    Также создает inline клавиатуру если есть совпадения по названию города.

    :param message: Message
    :param word: str
    :return: None
    """
    if message.text.isalpha():
        params = {'q': message.text.capitalize()}
        response = requests.request("GET", API.url1, headers=API.headers1, params=params)
        ssd = [x for x in response.json()['sr'] if x['type'] == 'CITY']
        logger.info('Делаем запрос к API по названию города.')

        if ssd:
            x = city_choice(word=word, ssd=ssd)
            bot.send_message(chat_id=message.chat.id, text='Выбери нужный город из списка', reply_markup=x)
            logger.info('Выводим найденные города.')

        else:
            bot.send_message(chat_id=message.chat.id, text='Этого города нет в списке. Введите другой город:')
            logger.info('Введен неизвестный город.')
    else:
        bot.send_message(chat_id=message.chat.id, text='Введите только буквы!')


def answer_user_photo(message, id_price, distance, data, user_id):
    """
    Делает запрос к API и выводит все найденные отели по заданным параметрам
    от пользователя. Также создает записи в базе данных.

    :param message: Message
    :param id_price: dict
    :param distance: list
    :param data: dict
    :param user_id: int
    :return: None
    """

    index = 0
    mess_db = User.create(command=data['command'], date=datetime.now().strftime('%d.%m.%Y - %H:%M:%S'),
                          user_id=user_id)
    for id_item, price in id_price.items():
        API.payload_detail['propertyId'] = id_item
        resp = requests.request("POST", API.url3, json=API.payload_detail, headers=API.headers2)
        name = resp.json()['data']['propertyInfo']['summary']['name']
        address = resp.json()['data']['propertyInfo']['summary']['location']['address']['firstAddressLine']
        result_text = f'Название отеля: {name}\nАдрес: {address}\nЦена за одну ночь: {price}' \
                      f'\nРасстояние до центра: {distance[index]} миль.'
        Hotel.create(name=name, address=address, price=price, distance=distance[index], req=mess_db)
        index += 1
        if data['photo_count'] == 0:
            bot.send_message(message.chat.id, text=result_text)

        else:
            count = 0
            media_group = []
            for num in range(int(data['photo_count'])):
                photo = resp.json()['data']['propertyInfo']['propertyGallery']['images'][num]['image']['url']
                media_group.append(types.InputMediaPhoto(photo, caption=result_text if count == 0 else ''))
                count += 1
            bot.send_media_group(chat_id=message.chat.id, media=media_group)
    logger.info('Сохраняем в базу данных информацию о пользователе и запрашиваемые им отели.')
