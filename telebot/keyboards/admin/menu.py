from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboard = InlineKeyboardMarkup()
keyboard.add(InlineKeyboardButton('Добавить пользователя', callback_data="user:create"))
keyboard.add(InlineKeyboardButton('Изменить пользователя', callback_data="user:edit"))
keyboard.add(InlineKeyboardButton('Удалить пользователя', callback_data="user:delete"))
