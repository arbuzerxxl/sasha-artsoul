import ujson
import requests
import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)
from telebot.loader import disp
from telebot.logger import bot_logger
from telebot.keyboards.callbacks import schedule_callback
from telebot.settings import URL
from telebot.handlers.utils import authentication


@disp.callback_query_handler(schedule_callback.filter(action="search"), state='*')
async def process_search_free_records(query: types.CallbackQuery, state: FSMContext):
    """Поиск доступных записей в БД на основе API."""

    await query.message.delete_reply_markup()

    bot_logger.info(f"[?] Обработка события: {query}")

    token = authentication()

    url = URL + "api/calendar/"
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    if re.search(r"удалить", query.message.html_text, ) or re.search(r"удалить", query.message.md_text):
        payload = None
    else:
        data = {"is_free": "False"}
        payload = ujson.dumps(data)
    response = requests.request("GET", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")
    if response.status_code == 200 and response.content:
        response_data = ujson.loads(response.content)
        record_display_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        if not response_data:
            await state.finish()
            msg = f"<b>В данный момент список записей в календаре пуст</b>"
            await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        else:
            for record in response_data:
                record_display = f"{record['master_full_name']}: {record['date_time']}"
                async with state.proxy() as state_data:
                    state_data[record_display] = record
                record_display_keyboard.add(KeyboardButton(record_display))
            msg = f"<i>Выберите запись в календаре</i>"
            await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=record_display_keyboard)
    else:
        await state.finish()
        msg = f"<code>Ошибка при вводе данных. Запрос отклонен: [{response.status_code}]</code>"
        await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML)
