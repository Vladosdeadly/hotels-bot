from loader import bot
from loguru import logger


def hotels_count(message, state):
    """
    Общее состояние для 3 основных команд.
    Запрашивает у пользователя, сколько человек будет проживать в номере отеля.

    :param message: Message
    :param state: State
    :return: None
    """
    if message.text.isdigit() and 0 < int(message.text) <= 5:
        bot.send_message(chat_id=message.chat.id, text='Сколько человек будет проживать?')
        bot.set_state(user_id=message.from_user.id, state=state, chat_id=message.chat.id)

        with bot.retrieve_data(user_id=message.from_user.id, chat_id=message.chat.id) as data:
            data['hotels_count'] = message.text
        logger.info('Сохраняем количество отелей и узнаем, сколько людей будет проживать.')
    else:
        bot.send_message(chat_id=message.chat.id, text='Некорректные данные.\nПожалуйста, повторите ввод:')


