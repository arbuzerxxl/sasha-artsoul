import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)
from telebot.handlers import delete_user, edit_user, schedule
from telebot.loader import disp, bot
from telebot.logger import bot_logger
from telebot.keyboards.callbacks import master_callback
from telebot.settings import URL
from telebot.handlers.utils import authorization


@disp.callback_query_handler(master_callback.filter(action="search"), state="*")
async def process_search_master(query: types.CallbackQuery, state: FSMContext):
    """Поиск мастера в БД на основе API."""

    await query.message.delete_reply_markup()

    bot_logger.info(f"[?] Обработка события: {query}")

    token = authorization()

    url = URL + "api/users/"
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    data = {"is_client": "False"}
    payload = ujson.dumps(data)
    response = requests.request("GET", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")
    if response.status_code == 200 and response.content:
        response_data = ujson.loads(response.content)
        users_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if not response_data:
            await state.finish()
            msg = f"<b>В данный момент список мастеров в БД пуст</b>"
            await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        for user in response_data:
            user_full_name = f"{user['last_name']} {user['first_name']}"
            async with state.proxy() as state_data:
                state_data[user_full_name] = user  # FIXME: слабое место, все пользователи помещаются в оперативную память, надо создать общий буфер при старте
            users_keyboard.add(KeyboardButton(user_full_name))
        msg = f"<i>Выберите мастера</i>"
        await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=users_keyboard)
    else:
        await state.finish()
        msg = f"<code>Ошибка при вводе данных. Запрос отклонен: [{response.status_code}]</code>"
        await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML)
