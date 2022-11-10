from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboard = InlineKeyboardMarkup()
keyboard.add(InlineKeyboardButton('Добавить пользователя', callback_data="user:create"))
