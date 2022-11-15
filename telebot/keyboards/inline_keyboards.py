from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

menu = InlineKeyboardMarkup()
menu.add(InlineKeyboardButton('Пользователи', callback_data="menu:users"))
menu.add(InlineKeyboardButton('Записи', callback_data="menu:visits"))
menu.add(InlineKeyboardButton('Расписание', callback_data="menu:schedule"))

user = InlineKeyboardMarkup()
user.add(InlineKeyboardButton('Клиенты', callback_data="users:clients"))
user.add(InlineKeyboardButton('Мастеры', callback_data="users:masters"))

search_user = InlineKeyboardMarkup()
search_user.add(InlineKeyboardButton('Продолжить', callback_data="users:search"))
search_user.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

search_master = InlineKeyboardMarkup()
search_master.add(InlineKeyboardButton('Продолжить', callback_data="masters:search"))
search_master.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

search_client = InlineKeyboardMarkup()
search_client.add(InlineKeyboardButton('Продолжить', callback_data="clients:search"))
search_client.add(InlineKeyboardButton('Отмена', callback_data="cancel:cancel"))

client = InlineKeyboardMarkup()
client.add(InlineKeyboardButton('Добавить клиента', callback_data="clients:create"))
client.add(InlineKeyboardButton('Изменить клиента', callback_data="clients:edit"))
client.add(InlineKeyboardButton('Удалить клиента', callback_data="clients:delete"))

master = InlineKeyboardMarkup()
master.add(InlineKeyboardButton('Добавить мастера', callback_data="masters:create"))
master.add(InlineKeyboardButton('Изменить мастера', callback_data="masters:edit"))
master.add(InlineKeyboardButton('Удалить мастера', callback_data="masters:delete"))

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
