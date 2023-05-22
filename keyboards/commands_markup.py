from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def photo_count(a):
    """
    Создает inline клавиатуру, чтобы узнать у пользователя нужно ли выводить фотографии.

    :param a: str
    :return: InlineKeyboardMarkup
    """
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Да', callback_data=a + '_yes'),
               InlineKeyboardButton(text='Нет', callback_data=a + '_no'))
    return markup


def city_choice(word, ssd):
    """
    Создает inline клавиатуру для выбора нужного города.

    :param word: str
    :param ssd: list
    :return: InlineKeyboardMarkup
    """
    ikm = InlineKeyboardMarkup()
    for x in ssd:
        ikm.add(InlineKeyboardButton(text=x['regionNames']['fullName'], callback_data=f'{word}{x["gaiaId"]}'))
    return ikm
