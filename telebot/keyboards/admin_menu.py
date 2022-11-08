from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboard = InlineKeyboardMarkup()
keyboard.add(InlineKeyboardButton('Здесь будет админ-команда', callback_data="nothing"))
