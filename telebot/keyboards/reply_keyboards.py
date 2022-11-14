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
).add(KeyboardButton('Имя')).add(KeyboardButton('Фамилия')).add(KeyboardButton('Пароль')).add(KeyboardButton('Статус')).add(KeyboardButton('Отмена'))

client_status_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(KeyboardButton('Постоянный клиент')).add(KeyboardButton('Обычный клиент')).add(KeyboardButton('Первый визит')).add(KeyboardButton('Отмена'))

master_status_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(KeyboardButton('Топ-мастер')).add(KeyboardButton('Обычный мастер')).add(KeyboardButton('Ученик')).add(KeyboardButton('Отмена'))

calendar_time_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(KeyboardButton('10:00')).add(KeyboardButton('12:00')).add(KeyboardButton('15:00')).add(KeyboardButton('17:00')).add(KeyboardButton('Свое'))
