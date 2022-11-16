from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

menu = InlineKeyboardMarkup()
menu.add(InlineKeyboardButton('Пользователи', callback_data="menu:users"))
menu.add(InlineKeyboardButton('Записи', callback_data="menu:visits"))
menu.add(InlineKeyboardButton('Расписание', callback_data="menu:schedule"))

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
