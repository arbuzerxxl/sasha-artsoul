from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

edit_user_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(KeyboardButton('Имя')).add(KeyboardButton('Фамилия')).add(KeyboardButton('Номер телефона')).add(KeyboardButton('Пароль')).add(KeyboardButton('Список'))
