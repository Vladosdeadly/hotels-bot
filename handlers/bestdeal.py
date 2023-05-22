from loader import bot
from telebot import types
import requests
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date, timedelta
from states.bestdeal_state import UserStateBestdeal
from api_requests.api import API, enter_api_parametres, get_city, answer_user_photo
from keyboards.commands_markup import photo_count
from commands_funcs.funcs import hotels_count
from keyboards.calendar import calendar_in, calendar_out
from loguru import logger


@bot.message_handler(commands=['bestdeal'])
def first_low(message: types.Message) -> None:
    """
    Обрабатывает команду bestdeal и начинает состояние.

    :param message: Message
    :return: None
    """
    API.payload['resultsSize'] = 200
    API.payload['sort'] = "DISTANCE"
    bot.set_state(user_id=message.from_user.id, state=UserStateBestdeal.city, chat_id=message.chat.id)
    logger.info('Запрошена команда bestdeal. Начинаем состояние.')
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        data['command'] = message.text
    bot.send_message(chat_id=message.chat.id, text='Введите город:')


@logger.catch()
@bot.message_handler(state=UserStateBestdeal.city)
def city(message: types.Message) -> None:
    """
    Принимает название города и делает запрос к API.

    :param message: Message
    :return: None
    """
    get_city(message=message, word='bestdeal_')


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith('bestdeal'))
def callback(call):
    """
    Обрабатывает callback и сохраняет id города.

    :param call: CallbackQuery
    :return: None
    """
    region_id = call.data.strip('bestdeal_')
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        data['regionId'] = region_id
    bot.set_state(user_id=call.from_user.id, state=UserStateBestdeal.price_min, chat_id=call.message.chat.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    bot.send_message(chat_id=call.from_user.id, text='Введите минимальную стоимость проживания:')
    logger.info('Сохраняем id нужного города и запрашиваем минимальную стоимость проживания.')


@logger.catch()
@bot.message_handler(state=UserStateBestdeal.price_min)
def min_price_func(message: types.Message) -> None:
    """
    Сохраняется минимальная стоимость проживания.

    :param message: Message
    :return: None
    """
    if message.text.isdigit():
        bot.send_message(chat_id=message.chat.id, text='Введите максимальную стоимость проживания:')
        bot.set_state(user_id=message.from_user.id, state=UserStateBestdeal.price_max, chat_id=message.chat.id)

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['price_min'] = message.text
        logger.info('Сохраняем минимальную стоимость проживания.')
    else:
        bot.send_message(chat_id=message.chat.id, text='Некорректные данные.\nПожалуйста, повторите ввод:')


@logger.catch()
@bot.message_handler(state=UserStateBestdeal.price_max)
def max_price_func(message: types.Message) -> None:
    """
    Сохраняется максимальная стоимость проживания.

    :param message: Message
    :return: None
    """
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        if message.text.isdigit():
            if int(message.text) > int(data['price_min']):
                bot.send_message(chat_id=message.chat.id, text='Введите минимальное расстояние до центра:')
                bot.set_state(user_id=message.from_user.id, state=UserStateBestdeal.distance_min,
                              chat_id=message.chat.id)
                data['price_max'] = message.text
                logger.info('Сохраняем максимальную стоимость проживания.')
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='Недопустимый диапазон цены.\nПожалуйста, повторите ввод:')
                logger.warning('Введен недопустимый диапазон цен.')
        else:
            bot.send_message(chat_id=message.chat.id, text='Некорректные данные.\nПожалуйста, повторите ввод:')


@logger.catch()
@bot.message_handler(state=UserStateBestdeal.distance_min)
def min_distance_func(message: types.Message) -> None:
    """
    Сохраняется минимальное расстояние до центра города.

    :param message: Message
    :return: None
    """
    if message.text.isdigit():
        bot.send_message(chat_id=message.chat.id, text='Введите максимальное расстояние до центра:')
        bot.set_state(user_id=message.from_user.id, state=UserStateBestdeal.distance_max, chat_id=message.chat.id)

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['distance_min'] = message.text
        logger.info('Сохраняем минимальное расстояние до центра города.')
    else:
        bot.send_message(chat_id=message.chat.id, text='Некорректные данные.\nПожалуйста, повторите ввод:')


@logger.catch()
@bot.message_handler(state=UserStateBestdeal.distance_max)
def max_distance_func(message: types.Message) -> None:
    """
    Сохраняется максимальное расстояние до центра города.

    :param message: Message
    :return: None
    """
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        if message.text.isdigit():
            if int(message.text) > int(data['distance_min']):
                bot.send_message(chat_id=message.chat.id, text='Теперь введите количество отелей(не больше 5):')
                bot.set_state(user_id=message.from_user.id, state=UserStateBestdeal.hotels_count,
                              chat_id=message.chat.id)
                data['distance_max'] = message.text
                logger.info('Сохраняем максимальное расстояние до центра города.')
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='Недопустимый диапазон расстояния.\nПожалуйста, повторите ввод:')
                logger.warning('Введен недопустимый диапазон расстояния.')
        else:
            bot.send_message(chat_id=message.chat.id, text='Некорректные данные.\nПожалуйста, повторите ввод:')


@logger.catch()
@bot.message_handler(state=UserStateBestdeal.hotels_count)
def get_hotels_count(message: types.Message) -> None:
    """
    Принимает и сохраняет количество выводимых отелей.

    :param message: Message
    :return: None
    """
    hotels_count(message=message, state=UserStateBestdeal.people_count)


@logger.catch()
@bot.message_handler(state=UserStateBestdeal.people_count)
def get_people_count(message: types.Message) -> None:
    """
    Создает календарь для получения даты заезда.

    :param message: Message
    :return: None
    """
    if message.text.isdigit():
        bot.send_message(chat_id=message.chat.id, text='Укажите дату заезда:')
        calendar_in(message=message, num=5)

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['people_count'] = message.text
    else:
        bot.send_message(chat_id=message.chat.id, text='Введите только цифры!')


@logger.catch()
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=5))
def cal(call):
    """
    Обрабатывает полученную дату и создает новый календарь
    для получения даты выезда.

    :param call: CallbackQuery
    :return: None
    """
    result = calendar_out(call=call, num=5)
    if result:

        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            a = str(result).split('-')
            data['date_in'] = {'d': a[2], 'm': a[1], 'y': a[0]}
            API.min_date = date(int(data['date_in']['y']), int(data['date_in']['m']), int(data['date_in']['d']))
            logger.info('Сохранили информацию о заезде при помощи календаря.')

            bot.send_message(chat_id=call.from_user.id, text='Укажите дату выезда:')
            calendar_in(message=call.message, num=6, min_date=API.min_date + timedelta(days=1),
                        max_date=API.min_date + timedelta(days=180))


@logger.catch()
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=6))
def calling(call):
    """
    Сохраняет полученную дату выезда и создает клавиатуру
    для вопроса пользователю, нужны ли фотографии.

    :param call: CallbackQuery
    :return: None
    """
    result = calendar_out(call, 6, min_date=API.min_date + timedelta(days=1),
                          max_date=API.min_date + timedelta(days=180))
    if result:

        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            a = str(result).split('-')
            data['date_out'] = {'d': a[2], 'm': a[1], 'y': a[0]}
            photo_markup = photo_count('right')
            bot.send_message(chat_id=call.from_user.id, text='Вывести фотографии отелей?', reply_markup=photo_markup)
        logger.info('Сохраняем дату выезда и спрашиваем, нужны ли фотографии.')


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith('right'))
def choice_photo(call: types.CallbackQuery):
    """
    Обрабатывает полученный ответ на вопрос про фотографии.
    Если ответ да, то переходит к следующему состоянию,
    если нет то выводит информацию и завершает текущее состояние.

    :param call: CallbackQuery
    :return: None
    """
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if call.data == 'right_yes':
        bot.send_message(chat_id=call.message.chat.id, text='Сколько фотографий вывести?(не больше 5)')
        bot.set_state(user_id=call.from_user.id, state=UserStateBestdeal.photo_count, chat_id=call.message.chat.id)
        logger.info('Фотографии нужны. Переходим к следующему состоянию.')

    elif call.data == 'right_no':
        bot.send_message(chat_id=call.message.chat.id, text='Значит без фотографий')
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            data['photo_count'] = 0

        enter_api_parametres(first_dict=API.payload, second_dict=data)
        API.payload['filters']['price']['min'] = int(data['price_min'])
        API.payload['filters']['price']['max'] = int(data['price_max'])

        response = requests.request("POST", API.url2, json=API.payload, headers=API.headers2)
        id_price = dict()
        distance = list()
        logger.info('Фотографии не нужны. Делаем запрос к API.')
        try:
            hotels = response.json()['data']['propertySearch']['properties']
            for el in hotels:
                if ',' in el['price']['options'][0]['formattedDisplayPrice']:
                    x = el['price']['options'][0]['formattedDisplayPrice'].replace(',', '.')
                    el['price']['options'][0]['formattedDisplayPrice'] = x
            need_list = [elem for elem in hotels
                         if int(data['price_min']) <= float(elem['price']['options'][0]['formattedDisplayPrice'].strip('$'))
                         <= int(data['price_max'])
                         and float(data['distance_min'])
                         <= float(elem['destinationInfo']['distanceFromDestination']['value'])
                         <= float(data['distance_max'])]

            if len(need_list) >= int(data['hotels_count']):
                length = int(data['hotels_count'])
            else:
                length = len(need_list)
                bot.send_message(call.message.chat.id, text=f'Найдено {length} отелей')
            for hotel in range(length):
                id_price[need_list[hotel]['id']] = need_list[hotel]['price']['options'][0]['formattedDisplayPrice']
                distance.append(need_list[hotel]['destinationInfo']['distanceFromDestination']['value'])

            answer_user_photo(message=call.message, id_price=id_price, distance=distance,
                              data=data, user_id=call.from_user.id)
        except TypeError:
            bot.send_message(chat_id=call.message.chat.id, text='Отелей по вашему запросу не найдено')
            logger.error('Отели не были найдены. Завершаем состояние.')

        bot.delete_state(call.from_user.id, call.message.chat.id)


@logger.catch()
@bot.message_handler(state=UserStateBestdeal.photo_count)
def photo_yes(message: types.Message) -> None:
    """
    Выводит пользователю всю информацию об отелях, включая фотографии.

    :param message: Message
    :return: None
    """
    if message.text.isdigit() and 0 < int(message.text) <= 5:

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['photo_count'] = message.text

        enter_api_parametres(first_dict=API.payload, second_dict=data)
        API.payload['filters']['price']['min'] = int(data['price_min'])
        API.payload['filters']['price']['max'] = int(data['price_max'])

        response = requests.request("POST", API.url2, json=API.payload, headers=API.headers2)
        id_price = dict()
        distance = list()
        logger.info('Делаем запрос к API.')
        try:
            hotels = response.json()['data']['propertySearch']['properties']
            for el in hotels:
                if ',' in el['price']['options'][0]['formattedDisplayPrice']:
                    x = el['price']['options'][0]['formattedDisplayPrice'].replace(',', '.')
                    el['price']['options'][0]['formattedDisplayPrice'] = x
            need_list = [elem for elem in hotels
                         if int(data['price_min']) <= float(elem['price']['options'][0]['formattedDisplayPrice'].strip('$'))
                         <= int(data['price_max'])
                         and float(data['distance_min'])
                         <= float(elem['destinationInfo']['distanceFromDestination']['value'])
                         <= float(data['distance_max'])]

            if len(need_list) >= int(data['hotels_count']):
                length = int(data['hotels_count'])
            else:
                length = len(need_list)
                bot.send_message(message.chat.id, text=f'Найдено {length} отелей')
            for hotel in range(length):
                id_price[need_list[hotel]['id']] = need_list[hotel]['price']['options'][0]['formattedDisplayPrice']
                distance.append(need_list[hotel]['destinationInfo']['distanceFromDestination']['value'])

            answer_user_photo(message=message, id_price=id_price,
                              distance=distance, data=data, user_id=message.from_user.id)
        except TypeError:
            bot.send_message(chat_id=message.chat.id, text='Отелей по вашему запросу не найдено')
            logger.error('Отели не были найдены. Завершаем состояние.')

        bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(chat_id=message.chat.id, text='Некорректные данные.\nПожалуйста, повторите ввод:')
