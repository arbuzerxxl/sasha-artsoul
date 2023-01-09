import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from loader import disp
from logger import bot_logger
from settings import URL
from handlers.utils import make_request
from keyboards.callbacks import visit_callback
from keyboards.inline_keyboards import search_schedule, search_user, month
from keyboards.reply_keyboards import statuses_keyboard, services_keyboard, discount_keyboard, continue_cancel_keyboard


class CreateVisit(StatesGroup):
    set_month = State()
    set_master = State()
    set_schedule_day = State()
    set_client = State()
    set_status = State()
    set_service = State()
    set_discount = State()
    request = State()


@disp.callback_query_handler(visit_callback.filter(action="create"))
async def process_create_visit(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await CreateVisit.set_month.set()

    msg = text(f"<i>Выберите месяц для поиска свободных окон в календаре: </i>")

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=month)


@disp.callback_query_handler(lambda c: re.fullmatch(pattern=r'^month:[\d]{1,2}$', string=c.data), state=CreateVisit.set_month)
async def process_set_month(query: types.CallbackQuery, state: FSMContext) -> types.Message:

    await query.message.delete_reply_markup()

    await CreateVisit.next()

    month = query.data.split(":")[1]

    async with state.proxy() as state_data:
        state_data["month"] = month

    msg = text(f"<i>Выберите мастера:</i>")

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML,
                               reply_markup=await search_user(user_type='master'))


@disp.callback_query_handler(lambda c: re.fullmatch(pattern=r'^([\d]{11}#([А-Я]{1}[а-яё]{2,15})\s([А-Я]{1}[а-яё]{2,15}))$',
                                                    string=c.data), state=CreateVisit.set_master)
async def process_set_data_master(query: types.CallbackQuery, state: FSMContext) -> types.Message:
    """Сохраняет данные о выбранном мастере в состояние"""

    await query.message.delete_reply_markup()

    await CreateVisit.next()

    master_phone, master_name = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        state_data["master_phone"] = master_phone
        state_data["master_name"] = master_name

        msg = text(f"<i>Выберите свободное окно в календаре:</i>")

        await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML,
                                   reply_markup=await search_schedule(master=state_data["master_phone"], month=state_data["month"]))


@disp.callback_query_handler(lambda c: re.fullmatch(
    pattern=r'^((0[1-9]{1}|[1-2]{1}[0-9]{1}|3[0-1]{1})-(0[1-9]{1}|1[1-2]{1})-20[\d]{2} [\d]{2}:[\d]{2}#[\d]{1,})$',
    string=c.data), state=CreateVisit.set_schedule_day)
async def process_set_schedule_day(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await CreateVisit.next()

    date_time, calendar_id = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        state_data['date_time'] = date_time
        state_data['calendar_id'] = calendar_id

    msg = "<i>Далее необходимо выбрать клиента:</i>"

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML,
                               reply_markup=await search_user(user_type='client'))


@disp.callback_query_handler(lambda c: re.fullmatch(pattern=r'^([\d]{11}#([А-Я]{1}[а-яё]{2,15})\s([А-Я]{1}[а-яё]{2,15}))$',
                                                    string=c.data), state=CreateVisit.set_client)
async def process_set_data_client(query: types.CallbackQuery, state: FSMContext) -> types.Message:
    """Сохраняет данные о выбранном клиенте в состояние"""

    await query.message.delete_reply_markup()

    await CreateVisit.next()

    client_phone, client_name = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        state_data["client_phone"] = client_phone
        state_data["client_name"] = client_name

        msg = "<i>Выберите тип записи:</i>"

        await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=statuses_keyboard)


@disp.message_handler(state=CreateVisit.set_status)
async def process_set_status(message: types.Message, state: FSMContext) -> types.Message:
    """Сохраняет выбранный статус в состояние"""

    async with state.proxy() as state_data:
        state_data['status'] = message.text

    await CreateVisit.set_service.set()

    msg = "<i>Выберите тип услуги:</i>"

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=services_keyboard)


@disp.message_handler(state=CreateVisit.set_service)
async def process_set_service(message: types.Message, state: FSMContext) -> types.Message:
    """Сохраняет выбранную услугу в состояние"""

    await CreateVisit.next()

    async with state.proxy() as state_data:
        state_data['service'] = message.text

    msg = "<i>Если необходимо, выберите тип скидки:</i>"

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=discount_keyboard)


@disp.message_handler(state=CreateVisit.set_discount)
async def process_set_discount(message: types.Message, state: FSMContext) -> types.Message:
    """Сохраняет выбранную скидку в состояние"""

    await CreateVisit.next()

    async with state.proxy() as state_data:
        if message.text == "Без скидки":
            state_data['discount'] = None
        else:
            state_data['discount'] = message.text

        msg = text("<i>Подтвердите данные:</i>",
                   f"<i>Клиент: <b>{state_data.get('client_name')}</b></i>",
                   f"<i>Мастер: <b>{state_data.pop('master_name')}</b></i>",
                   f"<i>Дата и время: <b>{state_data.get('date_time')}</b></i>",
                   f"<i>Статус: <b>{state_data.get('status')}</b></i>",
                   f"<i>Услуга: <b>{state_data.get('service')}</b></i>",
                   f"<i>Скидка: <b>{state_data.get('discount')}</b></i>",
                   sep='\n')

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=CreateVisit.request)
async def process_request_visit(message: types.Message, state: FSMContext):
    """Добавление новой записи в БД на основе API."""

    bot_logger.info(f"[?] Обработка события от {message.chat.last_name} {message.chat.first_name}")

    async with state.proxy() as state_data:
        client = state_data.pop('client_name')
        date_time = state_data.pop('date_time')

        data = {"calendar": state_data["calendar_id"],
                "status": state_data["status"],
                "service": state_data["service"],
                "client": state_data["client_phone"],
                "discount": state_data['discount']}

        response, status = await make_request(method="POST", url=(URL + 'api/visits/'),
                                              data=data)

        if status == 201 and response:

            bot_logger.info(f"[+] Запись {date_time} {client} успешно создана.")

            msg = text("<i>Запись успешно создана</i>",
                       f"<b>{date_time}</b>",
                       f"<b>{client}</b>",
                       sep='\n')

            await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

        elif status >= 400:

            for errors in response.values():
                for error in errors:
                    msg = f"<b>{error}</b>"
                    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

        else:

            bot_logger.info(f"[-] Попытка создать запись оказалась безуспешной [{status}]")
            msg = f"<code>Попытка создать запись оказалась безуспешной [{status}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

    await state.finish()
