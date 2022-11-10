import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import text, code
from telebot.settings import URL
from telebot.handlers.requests.user import authorization
from telebot.logger import bot_logger
from telebot.loader import disp
from telebot.handlers.admin import create_user, edit_user, delete_user
from telebot.keyboards.admin.user import edit_user_keyboard

USERKEYS = {
    'Имя': 'first_name',
    'Фамилия': 'last_name',
    'Номер телефона': 'phone_number',
    'Пароль': 'password'
}


@disp.message_handler(state=create_user.CreateUser.request)
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
                await message.answer(f"Ok, пользователь успешно добавлен!")
            else:
                await message.answer(f"Что-то пошло не так! Ошибка: [{response.status_code}]")
        else:
            bot_logger.info(f"[-] Отмена создания нового пользователя от [{message.from_id}].")
            await state.finish()
            await message.answer(f"Ок, данные о пользователе не будут занесены в БД.")


@disp.message_handler(state=edit_user.EditUser.check)
async def process_check_edit_user(message: types.Message, state: FSMContext):
    """Поиск пользователя в БД на основе API."""
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
            if len(response_data) == 1:
                state_data['id'] = response_data[0]['id']
                state_data['phone_number'] = response_data[0]['phone_number']
                await edit_user.EditUser.next()
                msg = text(f"<i>Пользователь {response_data[0]['first_name']} {response_data[0]['last_name']}.</i>"
                           "<i>Какие данные будем менять?</i>",
                           sep='\n')
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=edit_user_keyboard)
            else:
                bot_logger.debug(
                    f"Было найдено несколько пользователей по номеру {response_data[0]['phone_number']}, id: {[item['id'] for item in response_data]}"
                )
                await state.finish()
                msg = code("Было найдено несколько пользователей!")
                await message.answer(text=msg, parse_mode=types.ParseMode.MARKDOWN)
        else:
            await state.finish()
            msg = code(f"Что-то пошло не так! Ошибка: [{response.status_code}]")
            await message.answer(text=msg, parse_mode=types.ParseMode.MARKDOWN)


@disp.message_handler(state=edit_user.EditUser.request)
async def process_request_edit_user(message: types.Message, state: FSMContext):
    """Изменение пользователя в БД на основе API."""

    async with state.proxy() as state_data:

        url = URL + f"api/users/{state_data.pop('id')}/"

        if not state_data['user_data_key']:
            state_data.clear()  # TODO: дописать функцию если списком
        else:
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
        await message.answer(f"Ok, пользователь успешно изменен!")
    else:
        await message.answer(f"Что-то пошло не так! Ошибка: [{response.status_code}]")
