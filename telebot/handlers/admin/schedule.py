from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar
from telebot.loader import disp
from telebot.keyboards.reply_keyboards import calendar_time_keyboard, continue_cancel_keyboard


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
        if state_data["method"] == "create":
            await Schedule.set_master.set()
        elif state_data["method"] == "delete":
            await Schedule.delete_request.set()
        else:
            state.finish()
            msg = "<code>Метод не задан. Операция прекращена</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    if message.text == "Свое":
        msg = "<i>Введите время в формате HH:MM, например: 14:35</i>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
    else:
        async with state.proxy() as state_data:
            state_data['time'] = message.text
            msg = f"<i>Вы выбрали время <b>{message.text}</b></i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)
