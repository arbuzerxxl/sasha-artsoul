from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import locale
from datetime import datetime
from handlers.utils import make_request
from settings import URL


async def free_schedule_days():

    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

    month = datetime.now().month

    free_days = {}

    response, status = await make_request(method="GET",
                                          url=(URL + "api/calendar/"),
                                          data={"master": "89996453956",
                                                "is_free": True,
                                                "month": month})

    for calendar_day in response:

        if datetime.strptime(calendar_day["date_time"], "%d-%m-%Y %H:%M").timestamp() < datetime.now().timestamp():
            continue
        else:
            free_days[calendar_day["date_time"]] = calendar_day["id"]

    free_schedule_days = InlineKeyboardMarkup(row_width=3)

    for date, calendar_id in free_days.items():

        button = datetime.strptime(date, "%d-%m-%Y %H:%M").strftime("%d-%b %H:%M")

        free_schedule_days.insert(InlineKeyboardButton(f'{button}', callback_data=f"{date}#{calendar_id}"))

    return free_schedule_days


registration = InlineKeyboardMarkup()
registration.add(InlineKeyboardButton('Зарегистрироваться', callback_data="menu:registration"))

admin = InlineKeyboardMarkup()
admin.add(InlineKeyboardButton('Пользователи', callback_data="admin:users"))
admin.add(InlineKeyboardButton('Записи', callback_data="admin:visits"))
admin.add(InlineKeyboardButton('Расписание', callback_data="admin:schedule"))

menu = InlineKeyboardMarkup(row_width=2)
menu.insert(InlineKeyboardButton('Записаться на прием', callback_data="menu:appointment"))
menu.insert(InlineKeyboardButton('Отменить запись', callback_data="menu:cancel"))
menu.insert(InlineKeyboardButton('Активные записи', callback_data="menu:active"))
menu.insert(InlineKeyboardButton('История записей', callback_data="menu:history"))

user = InlineKeyboardMarkup(row_width=2)
user.insert(InlineKeyboardButton('Клиенты', callback_data="users:clients"))
user.insert(InlineKeyboardButton('Мастеры', callback_data="users:masters"))

search_user = InlineKeyboardMarkup(row_width=2)
search_user.insert(InlineKeyboardButton('Продолжить', callback_data="users:search"))
search_user.insert(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

search_schedule = InlineKeyboardMarkup(row_width=2)
search_schedule.insert(InlineKeyboardButton('Продолжить', callback_data="schedule:search"))
search_schedule.insert(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

client = InlineKeyboardMarkup()
client.add(InlineKeyboardButton('Добавить клиента', callback_data="clients:create"))
client.add(InlineKeyboardButton('Изменить клиента', callback_data="clients:edit"))
client.add(InlineKeyboardButton('Удалить клиента', callback_data="clients:delete"))

master = InlineKeyboardMarkup()
master.add(InlineKeyboardButton('Добавить мастера', callback_data="masters:create"))
master.add(InlineKeyboardButton('Изменить мастера', callback_data="masters:edit"))
master.add(InlineKeyboardButton('Удалить мастера', callback_data="masters:delete"))

schedule = InlineKeyboardMarkup(row_width=2)
schedule.insert(InlineKeyboardButton('Добавить в расписание', callback_data="schedule:create"))
schedule.insert(InlineKeyboardButton('Удалить из расписания', callback_data="schedule:delete"))

calendar = InlineKeyboardMarkup(row_width=2)
calendar.insert(InlineKeyboardButton('Обычный', callback_data="calendars:navigation"))
calendar.insert(InlineKeyboardButton('Детальный', callback_data="calendars:dialog"))

visit = InlineKeyboardMarkup()
visit.add(InlineKeyboardButton('Добавить запись', callback_data="visits:create"))
visit.add(InlineKeyboardButton('Изменить запись', callback_data="visits:edit"))
visit.add(InlineKeyboardButton('Удалить запись', callback_data="visits:delete"))
