from loader import bot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta


def calendar_in(message, num, min_date=date.today(), max_date=date.today() + timedelta(days=180)):
    """
    Первая часть календаря для пользователя.

    :param message: Message
    :param num: int
    :param min_date: datetime
    :param max_date: datetime
    :return: None
    """
    calendar, step = DetailedTelegramCalendar(calendar_id=num, min_date=min_date,
                                              max_date=max_date).build()
    bot.send_message(message.chat.id,
                     f"Select {LSTEP[step]}",
                     reply_markup=calendar)


def calendar_out(call, num, min_date=date.today(), max_date=date.today() + timedelta(days=180)):
    """
    Вторая часть календаря для пользователя.

    :param call: CallbackQuery
    :param num: int
    :param min_date: datetime
    :param max_date: datetime
    :return: datetime
    """
    result, key, step = DetailedTelegramCalendar(calendar_id=num, min_date=min_date,
                                                 max_date=max_date).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result}",
                              call.message.chat.id,
                              call.message.message_id)
        return result
