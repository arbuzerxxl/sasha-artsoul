import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import (State, StatesGroup)
from aiogram_calendar import (simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar)
from loader import disp
from logger import bot_logger
from settings import URL
from handlers.utils import make_request
from keyboards.reply_keyboards import calendar_time_keyboard, continue_cancel_keyboard
from keyboards.inline_keyboards import search_user


class Schedule(StatesGroup):
    set_time = State()
    set_master = State()
    create_request = State()


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

    await Schedule.set_master.set()

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

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=await search_user(user_type='master'))


@disp.callback_query_handler(lambda c: re.fullmatch(
    pattern=r'^([\d]{11}#([А-Я]{1}[а-яё]{2,15})\s([А-Я]{1}[а-яё]{2,15}))$',
    string=c.data), state=Schedule.create_request)
async def process_create_schedule(query: types.CallbackQuery, state: FSMContext):
    """Создает запись в расписании на основе API"""

    await query.message.delete_reply_markup()

    master_phone, master_name = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        date_time = state_data["date"] + " " + state_data["time"]

    response, status = await make_request(method="POST", url=(URL + "api/calendar/"), data={"date_time": date_time, "master": master_phone})

    if status > 400 and not response:

        msg = f"<code>Ошибка: [{status}]</code>"

    elif status == 400:

        msg = f"<b>Календарная запись уже существует</b>"

    elif response:
        bot_logger.info(f"[+] Запись {response['date_time']} {response['master_full_name']} создана в расписании</i>")
        msg = f"<i>Запись <b>{response['date_time']} {response['master_full_name']}</b>  создана в расписании</i>"

    else:
        msg = f"<code>Ошибка: [{status}]</code>"

    await state.finish()

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML)
