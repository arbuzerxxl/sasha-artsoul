import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import disp
from logger import bot_logger
from settings import URL
from handlers.utils import make_request
from keyboards.reply_keyboards import user_form_keyboard, client_status_keyboard, master_status_keyboard
from keyboards.inline_keyboards import search_user

API_FORM_KEYS = {
    'Имя': 'first_name',
    'Фамилия': 'last_name',
    'Номер телефона': 'phone_number',
    'TG ID': 'telegram_id'
}


class EditUser(StatesGroup):
    set_user = State()
    set_data = State()
    request = State()


@disp.callback_query_handler(lambda c: re.fullmatch(pattern=r'^(clients|masters):edit$', string=c.data))
async def process_edit_user(query: types.CallbackQuery, state: FSMContext) -> types.Message:
    """Выдает список доступных для изменения клиентов/мастеров"""

    await query.message.delete_reply_markup()

    URLS = {
        'clients': URL + "api/clients/",
        'masters': URL + "api/masters/"
    }

    async with state.proxy() as state_data:
        state_data['url'] = URLS.get(query.data.split(":")[0])
        state_data['user_type'] = URLS.get(query.data.split(":")[0][0:-1])

    await EditUser.set_user.set()

    msg = f"<i>Необходимо выбрать клиента</i>" if query.data.split(":")[0] == 'clients' else f"<i>Необходимо выбрать мастера</i>"

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=await search_user(user_type=query.data.split(":")[0][0:-1]))


@disp.callback_query_handler(lambda c: re.fullmatch(
    pattern=r'^([\d]{11}#([А-Я]{1}[а-яё]{2,15})\s([А-Я]{1}[а-яё]{2,15}))$',
    string=c.data), state=EditUser.set_user)
async def process_set_data_user(query: types.CallbackQuery, state: FSMContext) -> types.Message:
    """Сохраняет данные о выбранном пользователе в состояние"""

    await query.message.delete_reply_markup()

    user_phone, user_name = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        state_data["user_phone"] = user_phone
        state_data["user_name"] = user_name

    await EditUser.next()

    msg = "<i>Что будем менять?</i>"

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=user_form_keyboard)


@disp.message_handler(state=EditUser.set_data)
async def process_set_data_edit_user(message: types.Message, state: FSMContext) -> types.Message:
    """
    Если в качестве ключа выбрано поле "Статус",
    возвращает список доступных статусов для клиента/мастера.

    В ином случае, сохраняет ключ изменяемого поля в state и
    предлагает ввести новое значение для него.
    """

    await EditUser.next()

    async with state.proxy() as state_data:

        if message.text == "Статус":

            response, status = await make_request(method="GET", url=state_data['url'], data={'_user': state_data['user_phone']})

            state_data['detail_url'] = response[0]['detail_url']

            msg = f"<i>Выберите новый <b>{message.text}</b></i>"

            await message.answer(text=msg, parse_mode=types.ParseMode.HTML,
                                 reply_markup=client_status_keyboard if state_data["user_type"] == 'client' else master_status_keyboard)

        else:

            response, status = await make_request(method="GET", url=(URL + 'api/users/'), data={'_phone_number': state_data['user_phone']})

            state_data['detail_url'] = response[0]['detail_url']

            state_data['user_data_key'] = message.text

            msg = f"<i>Введите новые данные для: <b>{message.text}</b></i>"

            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=EditUser.request)
async def process_request_edit_user(message: types.Message, state: FSMContext) -> types.Message:
    """Изменяет данные пользователя посредством API"""

    bot_logger.info(f"[?] Обработка события от {message.chat.last_name} {message.chat.first_name}")

    async with state.proxy() as state_data:

        if message.text not in ['Постоянный клиент', 'Первый визит', 'Топ-мастер', 'Обычный мастер', 'Ученик']:

            response, status = await make_request(method="PATCH", url=state_data['detail_url'],
                                                  data={API_FORM_KEYS.get(state_data['user_data_key']): message.text})
        else:

            response, status = await make_request(method="PATCH", url=state_data['detail_url'],
                                                  data={'user_type': message.text})

        if status == 200 and response:

            bot_logger.info(f"[+] Данные пользователя {state_data['user_name']} успешно изменены")

            msg = "<i>Данные пользователя успешно изменены</i>"

            await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

        elif status >= 400:

            for errors in response.values():
                for error in errors:
                    msg = f"<b>{error}</b>"
                    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

        else:

            bot_logger.info(f"[-] Попытка изменить данные пользователя оказалась безуспешной [{status}]")
            msg = f"<code>Попытка изменить данные пользователя оказалась безуспешной [{status}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

    await state.finish()
