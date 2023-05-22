import atexit

from telebot import types
from telebot.custom_filters import StateFilter
from loader import bot
from utils.set_bot_commands import set_default_commands
import handlers
from database.history_classes import db, User, Hotel
from loguru import logger


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    """
    Обрабатывает команду start.

    :param message:
    :return: None
    """
    bot.send_message(message.chat.id, text='Добро пожаловать! Для просмотра команд введи /help.')


@bot.message_handler()
def any_text(message: types.Message):
    """
    Обрабатывает любое неизвестное боту сообщение, кроме запроса id пользователя.

    :param message:
    :return: None
    """
    if message.text == 'id':
        bot.send_message(message.chat.id, text=f'Твой id: {message.from_user.id}')
        logger.info('Был запрошен id пользователя.')
    else:
        bot.send_message(message.from_user.id,
                         text='Я не знаю такой команды. Введите /help для просмотра списка команд.')
        logger.info('Пользователь ввел неизвестное сообщение.')


@atexit.register
def goodbye() -> None:
    """
    Выводит сообщение при выходе
    """
    logger.info('Завершение работы бота.')


if __name__ == '__main__':
    logger.add('hotel_bot.log', rotation="100 MB", encoding='utf-8')
    logger.info('Запуск бота.')
    db.create_tables([User, Hotel])
    set_default_commands(bot)
    bot.add_custom_filter(StateFilter(bot))
    bot.polling(none_stop=True)
