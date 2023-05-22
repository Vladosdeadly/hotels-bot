from peewee import *


db = SqliteDatabase('data.db')


class BaseModel(Model):
    """
    Базовый класс для таблиц.
    """
    class Meta:
        database = db


class User(BaseModel):
    """
    Класс для создания таблицы, где будет храниться команда пользователя,
    дата и время ввода команды и id пользователя.
    """
    class Meta:
        db_table = 'users'
    command = CharField()
    date = CharField()
    user_id = IntegerField()


class Hotel(BaseModel):
    """
    Класс для создания таблицы отелей,
    которые вывелись пользователю в результате его запроса.
    """
    class Meta:
        db_table = 'hotels'
    name = CharField()
    address = CharField()
    price = CharField()
    distance = CharField()
    req = ForeignKeyField(User, related_name='hotels')
