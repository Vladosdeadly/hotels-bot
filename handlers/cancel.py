from loader import bot
from loguru import logger


@bot.message_handler(state='*', commands=['cancel'])
def any_state(message):
    """
    Функция, завершающая работу любого состояния.
    """
    bot.send_message(message.chat.id, "Вы вышли из цикла команды.")
    logger.info('Завершаем работу состояния командой cancel')
    bot.delete_state(message.from_user.id, message.chat.id)
