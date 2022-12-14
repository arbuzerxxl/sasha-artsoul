from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)


check_phone_number_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    KeyboardButton('Отправить свой контакт', request_contact=True)
)


yes_no_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    KeyboardButton('Да')
).add(
    KeyboardButton('Нет')
)

continue_cancel_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    KeyboardButton('Продолжить')
).add(
    KeyboardButton('Отмена')
)

user_form_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    KeyboardButton('Имя')
).add(
    KeyboardButton('Фамилия')
).add(
    KeyboardButton('TG ID')
).add(
    KeyboardButton('Статус')
).add(
    KeyboardButton('Отмена')
)

visit_form_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    KeyboardButton('Статус')
).add(
    KeyboardButton('Услуга')
).add(
    KeyboardButton('Скидка')
).add(
    KeyboardButton('Доп. плата')
).add(
    KeyboardButton('Комментарий')
).add(
    KeyboardButton('Рейтинг')
)

client_status_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    KeyboardButton('Постоянный клиент')
).add(
    KeyboardButton('Первый визит')
).add(
    KeyboardButton('Отмена')
)

master_status_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    KeyboardButton('Топ-мастер')
).add(
    KeyboardButton('Обычный мастер')
).add(
    KeyboardButton('Ученик')
).add(
    KeyboardButton('Отмена')
)

calendar_time_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    KeyboardButton('10:00')
).add(
    KeyboardButton('12:00')
).add(
    KeyboardButton('15:00')
).add(
    KeyboardButton('17:00')
).add(
    KeyboardButton('Свое')
)

statuses_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    KeyboardButton('Предварительная запись')
).add(
    KeyboardButton('Успешная запись')
)

services_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    KeyboardButton('Маникюр')
).add(
    KeyboardButton('Маникюр с покрытием')
).add(
    KeyboardButton('Коррекция')
).add(
    KeyboardButton('Наращивание')
).add(
    KeyboardButton('Френч')
).add(
    KeyboardButton('Педикюр')
).add(
    KeyboardButton('Педикюр с покрытием (стопа)')
).add(
    KeyboardButton('Педикюр с покрытием (пальчики)'))

discount_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).add(
    KeyboardButton('Первый визит')
).add(
    KeyboardButton('Шестой визит')
).add(
    KeyboardButton('Сарафан')
).add(
    KeyboardButton('Без скидки')
)
