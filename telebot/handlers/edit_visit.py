import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from loader import disp
from handlers.utils import make_request
from logger import bot_logger
from keyboards.callbacks import visit_callback
from keyboards.inline_keyboards import search_visit, search_user, visit_date
from keyboards.reply_keyboards import statuses_keyboard, services_keyboard, discount_keyboard, continue_cancel_keyboard, visit_form_keyboard


class EditVisit(StatesGroup):
    set_month = State()
    set_client = State()
    set_master = State()
    set_schedule_day = State()
    set_data = State()
    change_status = State()
    change_service = State()
    change_client = State()
    change_discount = State()
    change_extra_total = State()
    change_review = State()
    change_rating = State()
    request_visit = State()


@disp.callback_query_handler(visit_callback.filter(action="edit"))
async def process_edit_visit(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await EditVisit.set_month.set()

    msg = text(f"<i>Выберите месяц и год для поиска записи в календаре: </i>")

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=visit_date())


@disp.callback_query_handler(lambda c: re.fullmatch(pattern=r'^[\d]{1,2}#20[\d]{2}$', string=c.data), state=EditVisit.set_month)
async def process_set_month(query: types.CallbackQuery, state: FSMContext) -> types.Message:

    await query.message.delete_reply_markup()

    await EditVisit.next()

    month, year = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        state_data["month"] = month
        state_data["year"] = year

    msg = text(f"<i>Выберите клиента для поиска записи в календаре: </i>")

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML,
                               reply_markup=await search_user(user_type='client'))


@disp.callback_query_handler(lambda c: re.fullmatch(
    pattern=r'^([\d]{11}#([А-Я]{1}[а-яё]{2,15})\s([А-Я]{1}[а-яё]{2,15}))$',
    string=c.data), state=EditVisit.set_client)
async def process_set_data_client(query: types.CallbackQuery, state: FSMContext) -> types.Message:
    """Сохраняет данные о выбранном пользователе в состояние"""

    await query.message.delete_reply_markup()

    client_phone, client_name = tuple(query.data.split("#"))

    await EditVisit.next()

    async with state.proxy() as state_data:
        state_data["client_phone"] = client_phone
        state_data["client_name"] = client_name

        msg = text(f"<i>Выберите запись: </i>")

        await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML,
                                   reply_markup=await search_user(user_type='master'))


@disp.callback_query_handler(lambda c: re.fullmatch(pattern=r'^([\d]{11}#([А-Я]{1}[а-яё]{2,15})\s([А-Я]{1}[а-яё]{2,15}))$',
                                                    string=c.data), state=EditVisit.set_master)
async def process_set_data_master(query: types.CallbackQuery, state: FSMContext) -> types.Message:
    """Сохраняет данные о выбранном мастере в состояние"""

    await query.message.delete_reply_markup()

    await EditVisit.next()

    master_phone, master_name = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        state_data["master_phone"] = master_phone
        state_data["master_name"] = master_name

        msg = text(f"<i>Выберите запись:</i>")

        await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML,
                                   reply_markup=await search_visit(master=state_data["master_phone"],
                                                                   month=state_data["month"],
                                                                   client=state_data["client_phone"]))


@disp.callback_query_handler(lambda c: re.fullmatch(
    pattern=r'^visit#[\w\d\-\/\:]{1,}$',
    string=c.data), state=EditVisit.set_schedule_day)
async def process_set_schedule_day(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await EditVisit.next()

    detail_url = query.data.split("#")[1]

    async with state.proxy() as state_data:
        state_data["detail_url"] = detail_url

    msg = "<i>Что будем менять?</i>"

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=visit_form_keyboard)


@disp.message_handler(state=EditVisit.set_data)
async def process_set_data_edit_visit(message: types.Message, state: FSMContext) -> types.Message:
    """

    """

    STATES = {
        'Статус': EditVisit.change_status.set,
        'Услуга': EditVisit.change_service.set
    }

    await STATES[message.text]()

    msg = f"<i>Выберите новый <b>{message.text}</b></i>"

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML,
                         reply_markup=statuses_keyboard)


@disp.message_handler(state=EditVisit.change_status)
async def process_change_visit_status(message: types.Message, state: FSMContext) -> types.Message:

    async with state.proxy() as state_data:

        response, status = await make_request(method="PATCH", url=state_data['detail_url'], data={'status': message.text})

        if status == 200 and response:

            bot_logger.info(f"[+] Данные записи успешно изменены")

            msg = "<i>Данные записи успешно изменены</i>"

            await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

        elif status >= 400:

            for errors in response.values():
                for error in errors:
                    msg = f"<b>{error}</b>"
                    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

        else:

            bot_logger.info(f"[-] Попытка изменить запись оказалась безуспешной [{status}]")
            msg = f"<code>Попытка изменить запись оказалась безуспешной [{status}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

    await state.finish()
