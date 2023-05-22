from telebot.handler_backends import State, StatesGroup


class UserState1(StatesGroup):
    """
    Класс состояния для команды highprice.
    """
    city = State()
    hotels_count = State()
    people_count = State()
    photo = State()
    photo_count = State()
