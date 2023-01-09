import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from loader import disp, bot
from logger import bot_logger
from settings import URL
from handlers.utils import authentication
from keyboards.callbacks import visit_callback
from keyboards.inline_keyboards import search_schedule, search_visit, search_user, month
from keyboards.reply_keyboards import statuses_keyboard, services_keyboard, discount_keyboard, continue_cancel_keyboard


class CreateVisit(StatesGroup):
    set_month = State()
    set_client = State()
    set_schedule_day = State()
    set_client = State()
    set_status = State()
    set_service = State()
    set_discount = State()
    request_visit = State()


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

    msg = text(f"<i>Выберите клиента:</i>")

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML,
                               reply_markup=await search_user(user_type='client'))


@disp.callback_query_handler(lambda c: re.fullmatch(
    pattern=r'^([\d]{11}#([А-Я]{1}[а-яё]{2,15})\s([А-Я]{1}[а-яё]{2,15}))$',
    string=c.data), state=CreateVisit.set_client)
async def process_set_data_client(query: types.CallbackQuery, state: FSMContext) -> types.Message:
    """Сохраняет данные о выбранном пользователе в состояние"""

    await query.message.delete_reply_markup()

    client_phone, client_name = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        state_data["client_phone"] = client_phone
        state_data["client_name"] = client_name

        msg = text(f"<i>Выберите запись:</i>")

        await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML,
                                   reply_markup=await search_visit(client=client_phone, month=state_data["month"]))