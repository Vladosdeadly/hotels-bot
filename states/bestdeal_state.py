from telebot.handler_backends import State, StatesGroup


class UserStateBestdeal(StatesGroup):
    """
    Класс состояния для команды bestdeal.
    """
    city = State()
    price_min = State()
    price_max = State()
    distance_min = State()
    distance_max = State()
    hotels_count = State()
    people_count = State()
    photo = State()
    photo_count = State()
