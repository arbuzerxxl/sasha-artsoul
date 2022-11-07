from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

yes = KeyboardButton('Да')
no = KeyboardButton('Нет')

keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(yes).add(no)
