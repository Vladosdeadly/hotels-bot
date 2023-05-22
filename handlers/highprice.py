from loader import bot
from telebot import types
import requests
from telegram_bot_calendar import DetailedTelegramCalendar
from datetime import date, timedelta
from states.highprice_state import UserState1
from api_requests.api import API, enter_api_parametres, get_city, answer_user_photo
from keyboards.commands_markup import photo_count
from commands_funcs.funcs import hotels_count
from keyboards.calendar import calendar_in, calendar_out
from loguru import logger


@bot.message_handler(commands=['highprice'])
def first_low(message: types.Message) -> None:
    """
    Обрабатывает команду highprice и начинает состояние.

    :param message: Message
    :return: None
    """
    API.payload['filters']['price']['min'] = 10
    API.payload['filters']['price']['max'] = 20000
    API.payload['sort'] = "PRICE_LOW_TO_HIGH"
    API.payload['resultsSize'] = 200
    bot.set_state(user_id=message.from_user.id, state=UserState1.city, chat_id=message.chat.id)
    logger.info('Запрошена команда highprice. Начинаем состояние.')
    with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
        data['command'] = message.text

    bot.send_message(chat_id=message.chat.id, text='Введите город:')


@logger.catch()
@bot.message_handler(state=UserState1.city)
def city(message: types.Message) -> None:
    """
    Принимает название города и делает запрос к API.

    :param message: Message
    :return: None
    """
    get_city(message=message, word='City_id_')


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith('City_id'))
def callback(call):
    """
    Обрабатывает callback и сохраняет id города.

    :param call: CallbackQuery
    :return: None
    """
    region_id = call.data.strip('City_id_')
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
        data['regionId'] = region_id
    bot.set_state(user_id=call.from_user.id, state=UserState1.hotels_count, chat_id=call.message.chat.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    bot.send_message(chat_id=call.from_user.id, text='Теперь введите количество отелей(не больше 5):')
    logger.info('Сохраняем id нужного города и запрашиваем сколько отелей вывести.')


@logger.catch()
@bot.message_handler(state=UserState1.hotels_count)
def get_hotels_count(message: types.Message) -> None:
    """
    Принимает и сохраняет количество выводимых отелей.

    :param message: Message
    :return: None
    """
    hotels_count(message=message, state=UserState1.people_count)


@logger.catch()
@bot.message_handler(state=UserState1.people_count)
def get_people_count(message: types.Message) -> None:
    """
    Создает календарь для получения даты заезда.

    :param message: Message
    :return: None
    """
    if message.text.isdigit():
        bot.send_message(chat_id=message.chat.id, text='Укажите дату заезда:')
        calendar_in(message=message, num=3)

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['people_count'] = message.text
    else:
        bot.send_message(chat_id=message.chat.id, text='Некорректный ввод данных!')


@logger.catch()
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=3))
def cal(call):
    """
    Обрабатывает полученную дату и создает новый календарь
    для получения даты выезда.

    :param call: CallbackQuery
    :return: None
    """
    result = calendar_out(call=call, num=3)
    if result:

        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            a = str(result).split('-')
            data['date_in'] = {'d': a[2], 'm': a[1], 'y': a[0]}
            API.min_date = date(int(data['date_in']['y']), int(data['date_in']['m']), int(data['date_in']['d']))
            logger.info('Сохранили информацию о заезде при помощи календаря.')

            bot.send_message(chat_id=call.from_user.id, text='Укажите дату выезда:')
            calendar_in(message=call.message, num=4, min_date=API.min_date + timedelta(days=1),
                        max_date=API.min_date + timedelta(days=180))


@logger.catch()
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=4))
def calling(call):
    """
    Сохраняет полученную дату выезда и создает клавиатуру
    для вопроса пользователю, нужны ли фотографии.

    :param call: CallbackQuery
    :return: None
    """
    result = calendar_out(call, 4, min_date=API.min_date + timedelta(days=1),
                          max_date=API.min_date + timedelta(days=180))
    if result:

        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            a = str(result).split('-')
            data['date_out'] = {'d': a[2], 'm': a[1], 'y': a[0]}
            photo_markup = photo_count('Photo')
            bot.send_message(chat_id=call.from_user.id, text='Вывести фотографии отелей?', reply_markup=photo_markup)
        logger.info('Сохраняем дату выезда и спрашиваем, нужны ли фотографии.')


@logger.catch()
@bot.callback_query_handler(func=lambda call: call.data.startswith('Photo'))
def choice(call: types.CallbackQuery):
    """
    Обрабатывает полученный ответ на вопрос про фотографии.
    Если ответ да, то переходит к следующему состоянию,
    если нет то выводит информацию и завершает текущее состояние.

    :param call: CallbackQuery
    :return: None
    """
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
    if call.data == 'Photo_yes':
        bot.send_message(chat_id=call.message.chat.id, text='Сколько фотографий вывести?(не больше 5)')
        bot.set_state(user_id=call.from_user.id, state=UserState1.photo_count, chat_id=call.message.chat.id)
        logger.info('Фотографии нужны. Переходим к следующему состоянию.')

    elif call.data == 'Photo_no':
        bot.send_message(chat_id=call.message.chat.id, text='Значит без фотографий')
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            data['photo_count'] = 0

        enter_api_parametres(first_dict=API.payload, second_dict=data)

        response = requests.request("POST", API.url2, json=API.payload, headers=API.headers2)
        id_price = dict()
        distance = list()
        logger.info('Фотографии не нужны. Делаем запрос к API.')
        try:
            rev_list = response.json()['data']['propertySearch']['properties']
            rev_list.reverse()

            for hotel in rev_list[:int(data['hotels_count'])]:
                id_price[hotel['id']] = hotel['price']['options'][0]['formattedDisplayPrice']
                distance.append(hotel['destinationInfo']['distanceFromDestination']['value'])

            answer_user_photo(message=call.message, id_price=id_price, distance=distance,
                              data=data, user_id=call.from_user.id)

        except TypeError:
            bot.send_message(chat_id=call.message.chat.id, text='Отелей по вашему запросу не найдено')
            logger.error('Отели не были найдены. Завершаем состояние.')

        bot.delete_state(call.from_user.id, call.message.chat.id)


@logger.catch()
@bot.message_handler(state=UserState1.photo_count)
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

        response = requests.request("POST", API.url2, json=API.payload, headers=API.headers2)
        id_price = dict()
        distance = list()
        logger.info('Делаем запрос к API.')
        try:
            rev_list = response.json()['data']['propertySearch']['properties']
            rev_list.reverse()

            for hotel in rev_list[:int(data['hotels_count'])]:
                id_price[hotel['id']] = hotel['price']['options'][0]['formattedDisplayPrice']
                distance.append(hotel['destinationInfo']['distanceFromDestination']['value'])

            answer_user_photo(message=message, id_price=id_price,
                              distance=distance, data=data, user_id=message.from_user.id)
        except TypeError as q:
            bot.send_message(chat_id=message.chat.id, text='Отелей по вашему запросу не найдено')
            logger.error('Отели не были найдены. Завершаем состояние.')
        bot.delete_state(message.from_user.id, message.chat.id)

    else:
        bot.send_message(chat_id=message.chat.id, text='Некорректные данные.\nПожалуйста, повторите ввод:')
