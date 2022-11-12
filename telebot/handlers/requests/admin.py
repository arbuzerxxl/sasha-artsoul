import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import text
from telebot.settings import URL
from telebot.handlers.requests.user import authorization
from telebot.logger import bot_logger
from telebot.loader import disp
from telebot.handlers.admin import search_user, create_user, edit_user, delete_user
from telebot.keyboards.default import continue_cancel_keyboard

USERKEYS = {
    'Имя': 'first_name',
    'Фамилия': 'last_name',
    'Номер телефона': 'phone_number',
    'Пароль': 'password'
}


@disp.message_handler(state=create_user.CreateUser.request_data)
async def process_request_create_user(message: types.Message, state: FSMContext):
    """Добавление нового пользователя в БД на основе API."""
    async with state.proxy() as data:
        if message.text == 'Да':
            bot_logger.info(f"[?] Обработка события: {message}")

            token = authorization()

            url = URL + "api/users/"
            headers = {'Content-Type': 'application/json', 'Authorization': token}
            data = await state.get_data()
            payload = ujson.dumps(data)
            await state.finish()
            response = requests.request("POST", url, headers=headers, data=payload)
            bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}]. Содержимое: [{response.text}].")
            if response.status_code == 201 and response.content:
                msg = "<i>Ok, пользователь успешно добавлен!</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
            else:
                msg = f"<code>Что-то пошло не так! Ошибка: [{response.status_code}]</code>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        else:
            await state.finish()
            msg = "<i>Ок, данные о пользователе не будут занесены в БД.</i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=search_user.SearchUser.check)
async def process_check_user(message: types.Message, state: FSMContext):
    """Поиск пользователя в БД на основе API."""

    async with state.proxy() as state_data:
        method = state_data.pop('method')

    state.finish()

    if method == 'edit':  # TODO: подумать об реализации
        await edit_user.EditUser.select_change.set()
    else:
        await delete_user.DeleteUser.approve_deletion.set()

    async with state.proxy() as state_data:

        bot_logger.info(f"[?] Обработка события: {message}")

        token = authorization()

        url = URL + "api/users/"
        headers = {'Content-Type': 'application/json', 'Authorization': token}
        data = {'phone_number': str(message.text)}
        payload = ujson.dumps(data)

        response = requests.request("GET", url, headers=headers, data=payload)
        bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")
        if response.status_code == 200 and response.content:
            response_data = ujson.loads(response.content)
            if not response_data:
                await state.finish()
                msg = ("<code>Пользователь не найден! Попробуйте еще раз, вызвав меню админа повторно.</code>")
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
            elif len(response_data) > 1:
                bot_logger.debug(f"Найдено несколько пользователей по номеру {response_data[0]['phone_number']}, id: {[item['id'] for item in response_data]}")
                await state.finish()
                msg = "<code>Было найдено несколько пользователей!</code>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
            else:
                state_data['id'] = response_data[0]['id']
                state_data['phone_number'] = response_data[0]['phone_number']
                msg = f"<i>Пользователь <b>{response_data[0]['first_name']} {response_data[0]['last_name']}</b> найден.</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)

        else:
            await state.finish()
            msg = f"<code>Что-то пошло не так! Ошибка: [{response.status_code}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=edit_user.EditUser.request_data)
async def process_request_edit_user(message: types.Message, state: FSMContext):
    """Изменение пользователя в БД на основе API."""

    async with state.proxy() as state_data:

        url = URL + f"api/users/{state_data.pop('id')}/"
        user_data_key = USERKEYS.get(state_data.pop('user_data_key'))
        state_data[user_data_key] = message.text

    bot_logger.info(f"[?] Обработка события: {message}")

    token = authorization()

    headers = {'Content-Type': 'application/json', 'Authorization': token}
    data = await state.get_data()
    payload = ujson.dumps(data)
    await state.finish()
    response = requests.request("PATCH", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")
    if response.status_code == 200 and response.content:
        msg = "<i>Ok, пользователь успешно изменен!</i>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        bot_logger.debug(f"Response: {ujson.loads(response.content)}")  #FIXME: ошибка связанная с выводом response
    else:
        msg = f"<code>Что-то пошло не так! Ошибка: [{response.status_code}]</code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=delete_user.DeleteUser.request_delete)
async def process_request_delete_user(message: types.Message, state: FSMContext):
    """Удаление пользователя в БД на основе API."""

    async with state.proxy() as state_data:

        url = URL + f"api/users/{state_data.pop('id')}/"

    bot_logger.info(f"[?] Обработка события: {message}")

    token = authorization()

    headers = {'Content-Type': 'application/json', 'Authorization': token}
    data = await state.get_data()
    payload = ujson.dumps(data)
    await state.finish()
    response = requests.request("DELETE", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")
    if response.status_code == 204:
        msg = "<i>Ok, пользователь успешно удален!</i>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        bot_logger.debug(f"Response: {ujson.loads(response.content)}")
    else:
        msg = f"<code>Что-то пошло не так! Ошибка: [{response.status_code}]</code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
