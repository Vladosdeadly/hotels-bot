from loader import bot
from telebot import types
from database.history_classes import User, Hotel
from loguru import logger


@bot.message_handler(commands=['history'])
def first_low(message: types.Message) -> None:
    """
    Выводит пользователю все введенные им команды, а также информацию
    об отелях из базы данных.

    :param message: Message
    :return: None
    """
    logger.info('Запрошена команда history. Выводим историю запросов пользователя.')
    if not User.select().where(User.user_id == message.from_user.id):
        bot.send_message(message.chat.id, text='Ваша история пуста.')
        logger.warning('История пользователя пуста.')
    for user in User.select().where(User.user_id == message.from_user.id):
        bot.send_message(chat_id=message.chat.id,
                            text=f'Команда: {user.command}\nДата и время команды: {user.date}\nНайденные отели:')
        for hotel in Hotel.select().where(Hotel.req == user.id):
            bot.send_message(chat_id=message.chat.id,
                                text=f'Название отеля: {hotel.name}\n'
                                    f'Адрес: {hotel.address}\n'
                                    f'Цена за одну ночь: {hotel.price}\n'
                                    f'Расстояние до центра: {hotel.distance} миль')
