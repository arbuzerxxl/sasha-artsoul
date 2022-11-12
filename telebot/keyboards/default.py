from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

yes_no_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(KeyboardButton('Да')).add(KeyboardButton('Нет'))

continue_cancel_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(KeyboardButton('Продолжить')).add(KeyboardButton('Отмена'))

user_form_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(KeyboardButton('Имя')).add(KeyboardButton('Фамилия')).add(KeyboardButton('Пароль')).add(KeyboardButton('Отмена'))
