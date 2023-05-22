from loader import bot
from loguru import logger


@bot.message_handler(commands=['help'])
def help_user(message):
    """
    Функция, завершающая работу любого состояния.
    """

    text = """
    Команды бота:
    /lowprice - топ самых дешёвых отелей в городе
    /highprice - топ самых дорогих отелей в городе
    /bestdeal - топ отелей, наиболее подходящих по цене и расположению от центра
    /history - история поиска отелей
    /cancel - вернуться в начальное состояние
    """

    logger.info('Введена команда help')
    bot.send_message(message.chat.id, text=text)
