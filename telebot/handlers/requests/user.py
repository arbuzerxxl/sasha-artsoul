import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from telebot.settings import URL
from telebot.auth import auth_with_token
from telebot.logger import bot_logger
from telebot.loader import disp
from telebot.handlers.user.registration import RegistrationUser


def authentification():
    """Производит аутентификацию бота на основе jwt."""

    try:
        token = auth_with_token()
        return token
    except ValueError as wrong_user_data:
        bot_logger.exception(wrong_user_data)


@disp.message_handler(state=RegistrationUser.request)
async def add_user(message: types.Message, state: FSMContext):
    """Добавление нового пользователя в БД на основе API."""
    async with state.proxy() as data:
        if message.text == 'Да':
            bot_logger.info(f"[?] Обработка события: {message}")

            token = authentification()

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


@disp.message_handler(commands=['visits'])
async def show_visits(message: types.Message):
    """Отображание всех посещений."""

    bot_logger.info(f"[?] Обработка события: {message}")

    token = authentification()

    url = URL + "api/visits/"
    payload = {}
    headers = {'Authorization': token}
    response = requests.request("GET", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}]. Содержимое: [{response.text}].")
    if response.status_code == 200 and response.content:
        data = ujson.loads(response.content)
        await message.answer(text=f"Ok, данные получены {data}!")
