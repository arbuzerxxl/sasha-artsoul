import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import disp, bot
from logger import bot_logger
from settings import URL
from handlers.utils import authentication
from keyboards.callbacks import user_callback, client_callback, master_callback
from keyboards.reply_keyboards import user_form_keyboard, client_status_keyboard, master_status_keyboard
from keyboards.inline_keyboards import search_user

API_FORM_KEYS = {
    'Имя': 'first_name',
    'Фамилия': 'last_name',
    'Номер телефона': 'phone_number',
    'Пароль': 'password'
}


class EditUser(StatesGroup):
    select_change = State()
    set_data = State()
    request_user_data = State()
    request_check_and_change_status = State()


async def process_edit_set(msg: str, query: types.CallbackQuery) -> types.Message:
    """
    Удаляет предыдущую inline клавиатуру,
    назначает состояние EditUser в state_storage и
    перенаправляет в функцию поиска пользователей
    в БД: handlers/search_user.
    """

    await query.message.delete_reply_markup()

    await EditUser.select_change.set()

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=search_user)


@disp.callback_query_handler(user_callback.filter(action="edit"))
async def process_edit_user(query: types.CallbackQuery) -> types.Message:
    """
    Принимает запрос пользователя (users:edit).
    Чат-команда быстрого выхода из состояния - /cancel.
    """

    msg = "<i>Вы хотите изменить пользователя, верно?</i>"

    await process_edit_set(msg=msg, query=query)


@disp.callback_query_handler(client_callback.filter(action="edit"))
async def process_edit_client(query: types.CallbackQuery) -> types.Message:
    """То же, что и process_edit_user, но принимает запрос пользователя (clients:edit)."""

    msg = "<i>Вы хотите изменить клиента, верно?</i>"

    await process_edit_set(msg=msg, query=query)


@disp.callback_query_handler(master_callback.filter(action="edit"))
async def process_edit_master(query: types.CallbackQuery) -> types.Message:
    """То же, что и process_edit_user, но принимает запроспользователя (masters:edit)."""

    msg = "<i>Вы хотите изменить мастера, верно?</i>"

    await process_edit_set(msg=msg, query=query)


@disp.message_handler(state=EditUser.select_change)
async def process_select_change_edit_user(message: types.Message, state: FSMContext) -> types.Message:
    """
    Получает в state {'Петров Петр': {user_response_data}},
    сохраняет необходимые переменные в state для выбранного пользователя,
    выводит доступные ключи полей для их дальнейшего изменения.
    """

    async with state.proxy() as state_data:
        state_data['phone_number'] = state_data[message.text]['phone_number']
        state_data['full_name'] = message.text
        state_data['detail_url'] = state_data[message.text]['detail_url']

    await EditUser.set_data.set()

    msg = "<i>Что будем менять?</i>"

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=user_form_keyboard)


@disp.message_handler(state=EditUser.set_data)
async def process_set_data_edit_user(message: types.Message, state: FSMContext) -> types.Message:
    """
    Если в качестве ключа выбрано поле "Статус",
    возвращает список доступных статусов и назначает состояние смены статуса.

    В ином случае, сохраняет ключ изменяемого поля в state и
    предлагает ввести новое значение для него.
    """

    if message.text == "Статус":
        await EditUser.request_check_and_change_status.set()
        msg = f"<i>Выберите новый <b>{message.text}</b></i>"
        async with state.proxy() as state_data:
            if state_data["is_client"]:
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=client_status_keyboard)
            else:
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=master_status_keyboard)
    else:
        async with state.proxy() as state_data:
            state_data['user_data_key'] = message.text
            await EditUser.request_user_data.set()
            msg = f"<i>Введите новые данные для: <b>{message.text}</b></i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=EditUser.request_user_data)
async def process_request_edit_user(message: types.Message, state: FSMContext) -> types.Message:
    """Изменяет значение переданного в state поля посредством API"""

    bot_logger.info(f"[?] Обработка события от {message.chat.last_name} {message.chat.first_name}")

    async with state.proxy() as state_data:

        url = state_data['detail_url']
        data = {"phone_number": state_data["phone_number"], API_FORM_KEYS.get(state_data.pop('user_data_key')): message.text}

    token = authentication()

    headers = {'Content-Type': 'application/json', 'Authorization': token}

    payload = ujson.dumps(data)
    await state.finish()
    response = requests.request("PATCH", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")
    if response.status_code == 200 and response.content:
        msg = "<i>Пользователь успешно изменен!</i>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        response_data = ujson.loads(response.content)
        bot_logger.debug(f"[+] Пользователь изменен. ID: {response_data['id']}. TG: {response_data.get('telegram_id', None)}.")
    else:
        msg = f"<code>Ошибка при вводе данных. Запрос отклонен: [{response.status_code}]</code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=EditUser.request_check_and_change_status)
async def process_request_check_and_change_status_user(message: types.Message, state: FSMContext) -> types.Message:
    """
    Производит запрос на наличие в таблице Clients или Masters в БД выбранного пользователя и
    в случае успешного запроса изменяет 'Статус' посредством API
    """

    bot_logger.info(f"[?] Обработка события от {message.chat.last_name} {message.chat.first_name}")

    async with state.proxy() as state_data:

        if state_data["is_client"]:
            url = URL + "api/clients/"
        else:
            url = URL + "api/masters/"
        data = {'user': state_data['phone_number']}
        full_name = state_data['full_name']

    await state.finish()

    token = authentication()

    headers = {'Content-Type': 'application/json', 'Authorization': token}

    payload = ujson.dumps(data)

    response = requests.request("GET", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")
    if response.status_code == 200 and response.content:
        response_data = ujson.loads(response.content)
        data['user_type'] = message.text
        msg = f"<i>Статус пользователя <b>{full_name}</b> изменен на <b>{data['user_type']}</b></i>"

        if not response_data:
            response = requests.request("POST", url, headers=headers, data=payload)
        else:
            url = response_data[0]['detail_url']
            response = requests.request("PATCH", url, headers=headers, data=payload)

        if response.status_code == 200 and response.content:
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        else:
            msg = f"<code>Невозможно сменить статус для пользователя <b>{full_name}</b>! Ошибка: [{response.status_code}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
    else:
        msg = f"<code>Ошибка при вводе данных. Запрос отклонен: [{response.status_code}]</code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
