import os
import ujson
import aiohttp
from aiogram import types
from auth import auth_with_token
from logger import bot_logger
from loader import bot, DEBUG


async def sender_to_admin(msg: types.Message):
    """Отправляет оповещения админам."""

    if not DEBUG:  # TODO: заменить debug
        for admin in os.environ.get("TELEBOT_ADMINS").split(" "):
            await bot.send_message(text=msg, chat_id=int(admin))


async def authentication():
    """Производит аутентификацию бота на основе jwt."""

    try:
        token = await auth_with_token()
        return token
    except ValueError as wrong_user_data:
        bot_logger.exception(wrong_user_data)


async def make_request(method, url, data):

    token = await authentication()

    payload = ujson.dumps(data)

    async with aiohttp.ClientSession(trust_env=True) as session:

        headers = {'Content-Type': 'application/json', 'Authorization': token}

        if method == "GET":

            async with session.get(url, data=payload, headers=headers) as response:

                bot_logger.info(f"[?] URL: [{url}] Status: [{response.status}].")

                return await response.json(), response.status

        elif method == "POST":

            async with session.post(url, data=payload, headers=headers) as response:

                bot_logger.info(f"[?] URL: [{url}] Status: [{response.status}].")

                return await response.json(), response.status
