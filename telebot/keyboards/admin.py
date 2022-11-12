from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

menu = InlineKeyboardMarkup()
menu.add(InlineKeyboardButton('Пользователи', callback_data="menu:user"))
menu.add(InlineKeyboardButton('Записи', callback_data="menu:visits"))

user = InlineKeyboardMarkup()
user.add(InlineKeyboardButton('Добавить пользователя', callback_data="user:create"))
user.add(InlineKeyboardButton('Изменить пользователя', callback_data="user:edit"))
user.add(InlineKeyboardButton('Удалить пользователя', callback_data="user:delete"))

visit = InlineKeyboardMarkup()
visit.add(InlineKeyboardButton('Добавить запись', callback_data="visit:create"))
visit.add(InlineKeyboardButton('Изменить запись', callback_data="visit:edit"))
visit.add(InlineKeyboardButton('Удалить запись', callback_data="visit:delete"))
