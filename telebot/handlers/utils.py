import os
from aiogram import types
from telebot.auth import auth_with_token
from telebot.logger import bot_logger
from telebot.loader import bot, DEBUG


async def sender_to_admin(msg: types.Message):
    """Отправляет оповещения админам."""

    if not DEBUG:
        for admin in os.environ.get("TELEBOT_ADMINS").split(" "):
            await bot.send_message(text=msg, chat_id=int(admin))


def authentication():
    """Производит аутентификацию бота на основе jwt."""

    try:
        token = auth_with_token()
        return token
    except ValueError as wrong_user_data:
        bot_logger.exception(wrong_user_data)
