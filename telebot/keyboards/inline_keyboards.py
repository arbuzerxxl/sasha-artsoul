from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

menu = InlineKeyboardMarkup()
menu.add(InlineKeyboardButton('Пользователи', callback_data="menu:users"))
menu.add(InlineKeyboardButton('Записи', callback_data="menu:visits"))
menu.add(InlineKeyboardButton('Расписание', callback_data="menu:schedule"))

user = InlineKeyboardMarkup()
user.add(InlineKeyboardButton('Клиенты', callback_data="users:clients"))
user.add(InlineKeyboardButton('Мастеры', callback_data="users:masters"))


client = InlineKeyboardMarkup()
client.add(InlineKeyboardButton('Добавить клиента', callback_data="clients:create"))
client.add(InlineKeyboardButton('Изменить клиента', callback_data="users:edit"))
client.add(InlineKeyboardButton('Удалить клиента', callback_data="users:delete"))

master = InlineKeyboardMarkup()
master.add(InlineKeyboardButton('Добавить мастера', callback_data="masters:create"))
master.add(InlineKeyboardButton('Изменить мастера', callback_data="users:edit"))
master.add(InlineKeyboardButton('Удалить мастера', callback_data="users:delete"))


schedule = InlineKeyboardMarkup()
schedule.add(InlineKeyboardButton('Добавить в расписание', callback_data="schedule:create"))
schedule.add(InlineKeyboardButton('Удалить из расписания', callback_data="schedule:delete"))

calendar = InlineKeyboardMarkup()
calendar.add(InlineKeyboardButton('Обычный', callback_data="calendars:navigation"))
calendar.add(InlineKeyboardButton('Детальный', callback_data="calendars:dialog"))

visit = InlineKeyboardMarkup()
visit.add(InlineKeyboardButton('Добавить запись', callback_data="visits:create"))
visit.add(InlineKeyboardButton('Изменить запись', callback_data="visits:edit"))
visit.add(InlineKeyboardButton('Удалить запись', callback_data="visits:delete"))
