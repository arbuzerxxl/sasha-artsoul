import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from telebot.loader import disp, bot
from telebot.logger import bot_logger
from telebot.settings import URL
from telebot.handlers.utils import authentication
from telebot.keyboards.callbacks import visit_callback
from telebot.keyboards.inline_keyboards import search_schedule, search_user
from telebot.keyboards.reply_keyboards import statuses_keyboard, services_keyboard, discount_keyboard, continue_cancel_keyboard


class CreateVisit(StatesGroup):
    set_schedule_day = State()
    set_client = State()
    set_status = State()
    set_service = State()
    set_discount = State()
    request_visit = State()


@disp.callback_query_handler(visit_callback.filter(action="create"))
async def process_create_visit(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await CreateVisit.set_schedule_day.set()

    msg = text(f"<i>Вы хотите добавить новую запись, верно?</i>")

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=search_schedule)


@disp.message_handler(state=CreateVisit.set_schedule_day)
async def process_set_schedule_day(message: types.Message, state: FSMContext) -> types.Message:
    """

    """

    async with state.proxy() as state_data:
        state_data['calendar'] = state_data[message.text]['id']
        state_data['date_time'] = state_data[message.text]['date_time']
        state_data['master'] = state_data[message.text]['master_full_name']

    await CreateVisit.set_client.set()

    msg = "<i>Далее необходимо выбрать клиента</i>"

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=search_user)


@disp.message_handler(state=CreateVisit.set_client)
async def process_set_client(message: types.Message, state: FSMContext) -> types.Message:
    """

    """

    async with state.proxy() as state_data:
        state_data['client'] = state_data[message.text]['phone_number']
        state_data['client_name'] = message.text

    await CreateVisit.set_status.set()

    msg = "<i>Далее необходимо выбрать тип записи</i>"

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=statuses_keyboard)


@disp.message_handler(state=CreateVisit.set_status)
async def process_set_status(message: types.Message, state: FSMContext) -> types.Message:
    """

    """

    async with state.proxy() as state_data:
        state_data['status'] = message.text

    await CreateVisit.set_service.set()

    msg = "<i>Далее необходимо выбрать тип услуги</i>"

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=services_keyboard)


@disp.message_handler(state=CreateVisit.set_service)
async def process_set_service(message: types.Message, state: FSMContext) -> types.Message:
    """

    """

    async with state.proxy() as state_data:
        state_data['service'] = message.text

    await CreateVisit.request_visit.set()

    msg = "<i>Если необходимо, выберите тип скидки</i>"

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=discount_keyboard)


@disp.message_handler(state=CreateVisit.set_discount)
async def process_set_discount(message: types.Message, state: FSMContext) -> types.Message:
    """

    """

    async with state.proxy() as state_data:
        if message.text != "Без скидки":
            state_data['discount'] = None
        else:
            state_data['discount'] = message.text

        msg = text("<i>Подтвердите данные:</i>",
                   f"<i>Клиент: <b>{state_data.get('client_name')}</b></i>",
                   f"<i>Мастер: <b>{state_data.get('master')}</i></b>",
                   f"<i>Дата и время: <b>{state_data.get('date_time')}</b></i>",
                   f"<i>Услуга: <b>{state_data.get('service')}</b></i>",
                   f"<i>Скидка: <b>{state_data.get('discount')}</b></i>",
                   sep='\n')

        await CreateVisit.request_visit.set()

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=CreateVisit.request_visit)
async def process_request_visit(message: types.Message, state: FSMContext):
    """Добавление новой записи в БД на основе API."""

    bot_logger.info(f"[?] Обработка события: {message}")

    async with state.proxy() as state_data:
        client = state_data.pop('client_name')
        master = state_data.pop('master')
        date_time = state_data.pop('date_time')

        data = {"calendar": state_data["calendar"],
                "status": state_data["status"],
                "service": state_data["service"],
                "client": state_data["client"]}

    await state.finish()

    token = authentication()

    url = URL + "api/visits/"

    headers = {'Content-Type': 'application/json', 'Authorization': token}

    payload = ujson.dumps(data)

    response = requests.request("POST", url, headers=headers, data=payload)

    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")

    response_data = ujson.loads(response.content)

    if response.status_code == 201 and response.content:

        bot_logger.info(
            f"[+] Создана новая запись. Клиент: {client}, Мастер: {master}, Дата и время: {date_time}"
        )

        msg = text(f"<i>[{date_time}] Новая запись создана.</i>",
                   f"<i>Стоимость услуги: <b>{response_data['total']}</b></i>",
                   sep='\n')

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    else:
        bot_logger.debug("[!] Попытка зарегистрировать новую запись оказалась безуспешной.")
        msg = f"<code>Ошибка при вводе данных. Запрос отклонен: [{response.status_code}]</code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

        for error in response_data.values():
            msg = f"<b>{error[0]}</b>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
