from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(KeyboardButton('Да')).add(KeyboardButton('Нет'))
