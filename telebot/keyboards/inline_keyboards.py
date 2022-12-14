import locale
import calendar as clndr
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.utils import make_request
from settings import URL

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
MONTH = ('Янв', 'Февр', 'Март',
         'Апр', 'Май', 'Июнь',
         'Июль', 'Авг', 'Сент',
         'Окт', 'Нояб', 'Дек')


async def search_schedule(master: str = None, method: str = None, month: int = None) -> InlineKeyboardMarkup:

    month = month if month else datetime.now().month

    schedule_keyboard = InlineKeyboardMarkup(row_width=3)

    response, status = await make_request(method="GET", url=(URL + "api/calendar/"), data={"_master": master, "_is_free": True, "_month": month})

    if not response:

        schedule_keyboard.insert(InlineKeyboardButton('Доступных окон не найдено', callback_data="cancel:cancel"))

    elif status >= 400:

        for errors in response.values():
            for error in errors:
                schedule_keyboard.add(InlineKeyboardButton(f'{error}', callback_data="cancel:cancel"))

    elif status == 200 and response:

        free_days = []

        for calendar_day in response:

            if datetime.strptime(calendar_day["date_time"], "%d-%m-%Y %H:%M").timestamp() < datetime.now().timestamp():
                continue
            else:
                free_days.append((calendar_day["date_time"], calendar_day["id"], calendar_day["detail_url"]))

        for date_time, calendar_id, detail_url in free_days:

            button = datetime.strptime(date_time, "%d-%m-%Y %H:%M").strftime("%d-%b %H:%M")

            if method == 'delete':
                schedule_keyboard.insert(InlineKeyboardButton(f'{button}', callback_data=f"{date_time}#{detail_url}"))
            else:
                schedule_keyboard.insert(InlineKeyboardButton(f'{button}', callback_data=f"{date_time}#{calendar_id}"))

        schedule_keyboard.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

    else:

        schedule_keyboard.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

    return schedule_keyboard


async def search_user(user_type: str = None) -> InlineKeyboardMarkup:
    """Поиск пользователя в БД на основе API и вывод в окно в виде InlineKeyboard"""

    users_keyboard = InlineKeyboardMarkup(row_width=2)

    if not user_type:
        users_keyboard.insert(InlineKeyboardButton("Аргумент 'user' не указан", callback_data="cancel:cancel"))
        return users_keyboard

    if user_type == 'client':
        url = (URL + "api/clients/")
        inline_text = 'Клиентов не найдено'
    elif user_type == 'master':
        url = (URL + "api/masters/")
        inline_text = 'Мастеров не найдено'

    response, status = await make_request(method="GET", url=url)

    if status >= 400 or not response:

        users_keyboard.insert(InlineKeyboardButton(inline_text, callback_data="cancel:cancel"))

    elif response:

        for user in response:
            if user_type == 'client':
                user_full_name = user['pretty_client']
            if user_type == 'master':
                user_full_name = user['pretty_master']

            users_keyboard.insert(InlineKeyboardButton(text=user_full_name, callback_data=f"{user['user']}#{user_full_name}"))
        users_keyboard.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

    else:

        users_keyboard.add(InlineKeyboardButton(inline_text, callback_data="cancel:cancel"))

    return users_keyboard


async def search_visit(month: int = None, year: int = None, client: str = None, master: str = None, ) -> InlineKeyboardMarkup:
    """Поиск записи в БД на основе API и вывод в окно в виде InlineKeyboard"""

    visits_keyboard = InlineKeyboardMarkup()

    response, status = await make_request(method="GET", url=(URL + "api/visits/"), data={'_client': client, '_master': master,
                                                                                         '_month': month, '_year': year})

    if not response:

        visits_keyboard.insert(InlineKeyboardButton('Доступных записей не найдено', callback_data="cancel:cancel"))

    elif status == 200 and response:

        for visit in response:

            button = visit['pretty_calendar'].split(' Мастер: ')[0][6:]

            visits_keyboard.add(InlineKeyboardButton(f'{button}', callback_data=f"visit#{visit['detail_url']}"))

        visits_keyboard.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

    elif status >= 400:

        for errors in response.values():
            for error in errors:
                msg = f"<b>{error}</b>"
                visits_keyboard.add(InlineKeyboardButton(f'{msg}', callback_data="cancel:cancel"))

    else:

        visits_keyboard.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

    return visits_keyboard


def visit_date():

    now = datetime.now()

    visit_date = InlineKeyboardMarkup(row_width=3)

    visit_date.insert(InlineKeyboardButton(f"{MONTH[now.month]} {now.year}", callback_data=f"{now.month}#{now.year}"))

    for i in range(1, 6):

        year = now.year if now.month - i >= 0 else now.year - 1

        month = MONTH[now.month - i]

        visit_date.insert(InlineKeyboardButton(f"{month} {year}", callback_data=f"{MONTH.index(month) + 1}#{year}"))

    return visit_date


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
menu.add(InlineKeyboardButton('Выйти из меню', callback_data="cancel:cancel"))

user = InlineKeyboardMarkup(row_width=2)
user.insert(InlineKeyboardButton('Клиенты', callback_data="users:clients"))
user.insert(InlineKeyboardButton('Мастеры', callback_data="users:masters"))
user.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

client = InlineKeyboardMarkup(row_width=3)
client.insert(InlineKeyboardButton('Добавить', callback_data="clients:create"))
client.insert(InlineKeyboardButton('Изменить', callback_data="clients:edit"))
client.insert(InlineKeyboardButton('Удалить', callback_data="clients:delete"))
client.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

master = InlineKeyboardMarkup(row_width=3)
master.insert(InlineKeyboardButton('Добавить', callback_data="masters:create"))
master.insert(InlineKeyboardButton('Изменить', callback_data="masters:edit"))
master.insert(InlineKeyboardButton('Удалить', callback_data="masters:delete"))
master.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

schedule = InlineKeyboardMarkup(row_width=2)
schedule.insert(InlineKeyboardButton('Добавить в расписание', callback_data="schedule:create"))
schedule.insert(InlineKeyboardButton('Удалить из расписания', callback_data="schedule:delete"))
schedule.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

calendar = InlineKeyboardMarkup(row_width=2)
calendar.insert(InlineKeyboardButton('Обычный', callback_data="calendars:navigation"))
calendar.insert(InlineKeyboardButton('Детальный', callback_data="calendars:dialog"))
calendar.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

visit = InlineKeyboardMarkup()
visit.add(InlineKeyboardButton('Добавить запись', callback_data="visits:create"))
visit.add(InlineKeyboardButton('Изменить запись', callback_data="visits:edit"))
visit.add(InlineKeyboardButton('Удалить запись', callback_data="visits:delete"))
visit.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

month = InlineKeyboardMarkup(row_width=3)

for i in range(1, 13):
    month.insert(InlineKeyboardButton(MONTH[i - 1], callback_data=f"month:{i}"))
