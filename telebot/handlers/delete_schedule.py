import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import (State, StatesGroup)
from loader import disp, bot
from logger import bot_logger
from settings import URL
from handlers.utils import authentication
from keyboards.callbacks import schedule_callback
from keyboards.reply_keyboards import calendar_time_keyboard, continue_cancel_keyboard
from keyboards.inline_keyboards import search_schedule


class ScheduleDelete(StatesGroup):
    approve_deletion = State()
    request_delete = State()


@disp.callback_query_handler(schedule_callback.filter(action="delete"))
async def process_delete_schedule(query: types.CallbackQuery, state: FSMContext):
    """Удаление записей в календаре на основе API."""

    await query.message.delete_reply_markup()

    await ScheduleDelete.approve_deletion.set()

    msg = "<i>Вы хотите удалить запись из календаря, верно?</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=search_schedule)


@disp.message_handler(state=ScheduleDelete.approve_deletion)
async def process_approve_deletion_user(message: types.Message, state: FSMContext) -> types.Message:
    """

    """

    await ScheduleDelete.next()

    async with state.proxy() as state_data:
        state_data['detail_url'] = state_data[message.text]['detail_url']
        state_data['master_full_name'] = state_data[message.text]['master_full_name']
        state_data['date_time'] = state_data[message.text]['date_time']

    msg = "<i>Уверены, что хотите удалить запись?</i>"
    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=ScheduleDelete.request_delete)
async def process_delete_schedule(message: types.Message, state: FSMContext):
    """Удаляет запись из расписания на основе API"""

    bot_logger.info(f"[?] Обработка события: {message}")

    token = authentication()

    headers = {'Content-Type': 'application/json', 'Authorization': token}

    async with state.proxy() as state_data:

        url = state_data['detail_url']

        response = requests.request("DELETE", url, headers=headers, data=None)
        bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")
        if response.status_code == 204:
            msg = "<i>Запись успешно удалена!</i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
            bot_logger.debug(f"[+] Запись удалена. Дата и время: {state_data['date_time']}. Мастер: {state_data['master_full_name']}")
        else:
            msg = f"<code>Ошибка при вводе данных. Запрос отклонен: [{response.status_code}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
            bot_logger.debug(f"[!] Запись не может быть удалена. Ошибка запроса: {response.status_code}")

    await state.finish()
