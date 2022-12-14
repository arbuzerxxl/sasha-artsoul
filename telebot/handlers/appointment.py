import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from loader import disp, bot
from logger import bot_logger
from settings import URL
from keyboards.callbacks import menu_callbalck
from keyboards.inline_keyboards import search_user, search_schedule
from keyboards.reply_keyboards import services_keyboard, continue_cancel_keyboard
from handlers.utils import make_request


class Appointment(StatesGroup):
    set_service = State()
    set_master = State()
    set_schedule_day = State()
    request = State()


@disp.callback_query_handler(menu_callbalck.filter(action="appointment"))
async def process_create_appointment(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await Appointment.set_service.set()

    response, status = await make_request(method="GET", url=(URL + "api/users/"), data={"_telegram_id": query.message.chat.id})

    if status == 200 and response:

        async with state.proxy() as state_data:
            state_data['client'] = response[0]['phone_number']

        msg = text(f"<i>Пожалуйста, выберите услугу:</i>")

        await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=services_keyboard)

    else:
        msg = text("<i>Я не смог идентифицировать Вас как нашего клиента</i>",
                   "Пожалуйста, пройдите регистрацию",
                   sep="\n")

        await state.finish()

        await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=Appointment.set_service)
async def process_set_service(message: types.Message, state: FSMContext) -> types.Message:

    await Appointment.next()

    async with state.proxy() as state_data:
        state_data['service'] = message.text

    msg = "<i>Выберите своего мастера:</i>"

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=await search_user(user_type='master'))


@disp.callback_query_handler(lambda c: re.fullmatch(
    pattern=r'^([\d]{11}#([А-Я]{1}[а-яё]{2,15})\s([А-Я]{1}[а-яё]{2,15}))$',
    string=c.data), state=Appointment.set_master)
async def process_set_master_schedule(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await Appointment.next()

    master_phone, master_name = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        state_data['master_phone'] = master_phone
        state_data['master'] = master_name

    msg = text(f"<i>Выберите дату и время</i>")

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML,
                           reply_markup=await search_schedule(master=master_phone))


@disp.callback_query_handler(lambda c: re.fullmatch(
    pattern=r'^((0[1-9]{1}|[1-2]{1}[0-9]{1}|3[0-1]{1})-(0[1-9]{1}|1[1-2]{1})-20[\d]{2} [\d]{2}:[\d]{2}#[\d]{1,})$',
    string=c.data), state=Appointment.set_schedule_day)
async def process_set_schedule_day(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await Appointment.next()

    date_time, calendar_id = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        state_data['date_time'] = date_time
        state_data['calendar_id'] = calendar_id

    msg = text("<i>Подтвердите данные:</i>",
               f"<i>Услуга: <b>{state_data.get('service')}</b></i>",
               f"<i>Мастер: <b>{state_data.get('master')}</b></i>",
               f"<i>Дата и время: <b>{state_data.get('date_time')}</b></i>",
               sep='\n')

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=Appointment.request)
async def process_request_appointment(message: types.Message, state: FSMContext):
    """Запрос на создание записи от клиента"""

    bot_logger.info(f"[?] Обработка события от {message.chat.last_name} {message.chat.first_name}")

    async with state.proxy() as state_data:

        data = {"calendar": state_data["calendar_id"],
                "service": state_data["service"],
                "client": state_data["client"]}

    await state.finish()

    response, status = await make_request(method="POST", url=(URL + "api/visits/"), data=data)

    if status == 201 and response:

        bot_logger.info(f"[+] Создана новая запись: {response['pretty_calendar']} Клиент: {response['client']}")

        msg = text("<i>Новая запись создана.</i>",
                   f"<i>{response['pretty_calendar']}</i>",
                   f"<i>Услуга: <b>{response['service']}</b></i>",
                   f"<i>Стоимость услуги: <b>{response['total']}</b></i>",
                   sep='\n')

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    elif status >= 400:

        for errors in response.values():
            for error in errors:
                msg = f"<b>{error}</b>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    else:
        bot_logger.debug("[!] Попытка зарегистрировать новую запись оказалась безуспешной.")
        msg = text("<i>На данный момент я не могу записать Вас на прием.</i>",
                   sep="\n")
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
