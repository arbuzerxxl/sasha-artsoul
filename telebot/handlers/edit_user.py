import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from telebot.loader import disp, bot
from telebot.logger import bot_logger
from telebot.settings import URL
from telebot.handlers.utils import authorization
from telebot.keyboards.callbacks import user_callback, client_callback, master_callback
from telebot.keyboards.reply_keyboards import user_form_keyboard, client_status_keyboard, master_status_keyboard
from telebot.keyboards.inline_keyboards import search_user, search_client, search_master

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


@disp.callback_query_handler(user_callback.filter(action="edit"))
async def process_edit_user(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await EditUser.select_change.set()

    async with state.proxy() as state_data:
        state_data['method'] = 'edit_user'
    msg = "<i>Вы хотите изменить пользователя, верно?</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=search_user)


@disp.callback_query_handler(client_callback.filter(action="edit"))
async def process_edit_client(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await EditUser.select_change.set()

    async with state.proxy() as state_data:
        state_data['method'] = 'edit_client'
    msg = "<i>Вы хотите изменить клиента, верно?</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=search_client)


@disp.callback_query_handler(master_callback.filter(action="edit"))
async def process_edit_master(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await EditUser.select_change.set()

    async with state.proxy() as state_data:
        state_data['method'] = 'edit_master'
    msg = "<i>Вы хотите изменить мастера, верно?</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=search_master)


@disp.message_handler(state=EditUser.select_change)
async def process_select_change_edit_user(message: types.Message, state: FSMContext):

    async with state.proxy() as state_data:
        state_data['phone_number'] = state_data[message.text]['phone_number']
        state_data['full_name'] = message.text
        state_data['detail_url'] = state_data[message.text]['detail_url']
        state_data['is_client'] = state_data[message.text]['is_client']

    await EditUser.set_data.set()
    msg = "<i>Что будем менять?</i>"
    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=user_form_keyboard)


@disp.message_handler(state=EditUser.set_data)
async def process_set_data_edit_user(message: types.Message, state: FSMContext):

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
async def process_request_edit_user(message: types.Message, state: FSMContext):
    """Изменение пользователя в БД на основе API."""

    bot_logger.info(f"[?] Обработка события: {message}")

    async with state.proxy() as state_data:

        url = state_data['detail_url']
        data = {"phone_number": state_data["phone_number"], API_FORM_KEYS.get(state_data.pop('user_data_key')): message.text}

    token = authorization()

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
async def process_request_check_and_change_status_user(message: types.Message, state: FSMContext):
    """Проверка статуса пользователя (клиент/мастер/none) в БД на основе API."""

    bot_logger.info(f"[?] Обработка события: {message}")

    async with state.proxy() as state_data:

        if state_data["is_client"]:
            url = URL + "api/clients/"
        else:
            url = URL + "api/masters/"
        data = {'user': state_data['phone_number']}
        full_name = state_data['full_name']

    await state.finish()

    token = authorization()

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
