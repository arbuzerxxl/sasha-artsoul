import ujson
import requests
import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton)
from loader import disp
from logger import bot_logger
from keyboards.callbacks import user_callback
from settings import URL
from handlers.utils import authentication, make_request


@disp.callback_query_handler(user_callback.filter(action="search"), state='*')
async def process_search_user(query: types.CallbackQuery, state: FSMContext):
    """Поиск пользователя в БД на основе API."""

    await query.message.delete_reply_markup()

    if re.search(r"клиент", query.message.html_text, ) or re.search(r"клиент", query.message.md_text):
        data = {"is_client": "True"}
        url = (URL + "api/users/")
    elif re.search(r"мастер", query.message.html_text) or re.search(r"мастер", query.message.md_text):
        data = None
        url = (URL + "api/masters/")
    else:
        url = None
        data = None

    response, status = await make_request(method="GET", url=url, data=data)

    if status == 200 and response:

        # users_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        # if not response:
        #     await state.finish()
        #     msg = f"<b>В данный момент список пользователей в БД пуст</b>"
        #     await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        # for user in response:
        #     user_full_name = f"{user['last_name']} {user['first_name']}"
        #     async with state.proxy() as state_data:
        #         state_data[user_full_name] = user  # FIXME: слабое место, все пользователи помещаются в оперативную память, надо создать общий буфер при старте
        #     users_keyboard.add(KeyboardButton(user_full_name))

        users_keyboard = InlineKeyboardMarkup()

        for user in response:
            if "pretty_master" in user:
                user_full_name = user['pretty_master']
            if "last_name" in user and "first_name" in user:
                user_full_name = f"{user['last_name']} {user['first_name']}"
            users_keyboard.add(InlineKeyboardButton(text=user_full_name, callback_data=f"{user['user']}#{user_full_name}"))

        msg = f"<i>Выберите пользователя</i>"

        await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=users_keyboard)

    elif not response:

        await state.finish()
        msg = f"<b>В данный момент список пользователей в БД пуст</b>"
        await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    else:

        await state.finish()

        msg = f"<code>Ошибка при вводе данных. Запрос отклонен: [{response.status_code}]</code>"

        await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML)
