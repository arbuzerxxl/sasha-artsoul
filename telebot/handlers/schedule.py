import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import (State, StatesGroup)
from aiogram_calendar import (simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar)
from telebot.loader import disp
from telebot.logger import bot_logger
from telebot.settings import URL
from telebot.handlers.utils import authentication
from telebot.keyboards.reply_keyboards import calendar_time_keyboard, continue_cancel_keyboard
from telebot.keyboards.inline_keyboards import search_user


class Schedule(StatesGroup):
    set_time = State()
    set_master = State()
    create_request = State()
    delete_request = State()


@disp.callback_query_handler(simple_cal_callback.filter())
async def process_set_date_schedule_from_simple_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):

    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy() as state_data:
            state_data['date'] = date.strftime("%Y-%m-%d")
            await Schedule.set_time.set()
            await callback_query.message.answer(
                f'Вы выбрали: {date.strftime("%d/%m/%Y")}',
                reply_markup=calendar_time_keyboard)


@disp.callback_query_handler(dialog_cal_callback.filter())
async def process_set_date_schedule_from_dialog_calendar(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):

    selected, date = await DialogCalendar().process_selection(callback_query, callback_data)
    if selected:
        async with state.proxy() as state_data:
            state_data['date'] = date.strftime("%d-%m-%Y ")
            await Schedule.set_time.set()
            await callback_query.message.answer(
                f'Вы выбрали: {date.strftime("%d/%m/%Y")}',
                reply_markup=calendar_time_keyboard)


@disp.message_handler(state=Schedule.set_time)
async def process_set_time_schedule(message: types.Message, state: FSMContext):

    async with state.proxy() as state_data:
        if state_data["method"] == "create_schedule":
            await Schedule.set_master.set()
        elif state_data["method"] == "delete_schedule":
            await Schedule.delete_request.set()

    if message.text == "Свое":
        msg = "<i>Введите время в формате HH:MM, например: 14:35</i>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
    else:
        async with state.proxy() as state_data:
            state_data['time'] = message.text
            msg = f"<i>Вы выбрали время <b>{message.text}</b></i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=Schedule.set_master)
async def process_set_master_schedule(message: types.Message, state: FSMContext):

    await Schedule.create_request.set()

    async with state.proxy() as state_data:
        state_data.setdefault('time', message.text)

    msg = f"<i>Необходимо назначить мастера</i>"

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=search_user)


@disp.message_handler(state=Schedule.create_request)
async def process_create_schedule(message: types.Message, state: FSMContext):
    """Создает запись из расписания на основе API"""

    bot_logger.info(f"[?] Обработка события: {message}")

    async with state.proxy() as state_data:
        state_data.setdefault('time', message.text)
        state_data['phone_number'] = state_data[message.text]['phone_number']
        state_data['full_name'] = message.text
        state_data['detail_url'] = state_data[message.text]['detail_url']

    token = authentication()

    url = URL + "api/calendar/"

    headers = {'Content-Type': 'application/json', 'Authorization': token}

    async with state.proxy() as state_data:

        data = {"date_time": state_data["date"] + " " + state_data["time"], "master": state_data['phone_number']}

        payload = ujson.dumps(data)
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 201 and response.content:
            response_data = ujson.loads(response.content)
            msg = f"<i>Запись <b>[{response_data['date_time']}] [{state_data['full_name']}]</b> создана в расписании</i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
            await state.finish()
        else:
            msg = f"<code>Ошибка: [{response.status_code}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=Schedule.delete_request)
async def process_delete_schedule(message: types.Message, state: FSMContext):
    """Удаляет запись из расписания на основе API"""

    bot_logger.info(f"[?] Обработка события: {message}")

    token = authentication()

    url = URL + "api/calendar/"

    headers = {'Content-Type': 'application/json', 'Authorization': token}

    async with state.proxy() as state_data:

        state_data.setdefault("time", message.text)

        data = {"date_time": state_data["date"] + " " + state_data["time"]}

        payload = ujson.dumps(data)
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200 and response.content:
            response_data = ujson.loads(response.content)
            if not response_data:
                msg = f"<i>Запись <b>[{data['date_time']}]</b> не найдена в расписании</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
                await state.finish()
            else:
                msg = f"<i>Запись <b>[{data['date_time']}]</b> найдена в расписании</i>"
                url = response_data[0]['detail_url']
                response = requests.request("DELETE", url, headers=headers, data=None)
                if response.status_code == 204:
                    msg = f"<i>Запись <b>[{data['date_time']}]</b> успешно удалена из расписания!</i>"
                    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
                    bot_logger.debug(f"[+] Запись <b>[{data['date_time']}]</b> успешно удалена из расписания.")
                else:
                    msg = f"<code>Что-то пошло не так! Ошибка: [{response.status_code}]</code>"
                    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
                    bot_logger.debug(f"[!] Запись <b>[{data['date_time']}]</b> не может быть удалена из расписания. Ошибка запроса: {response.status_code}")
        else:
            msg = f"<code>Ошибка при вводе данных. Запрос отклонен: [{response.status_code}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
