import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from telebot.settings import URL
from telebot.auth import auth_with_token
from telebot.logger import bot_logger
from telebot.loader import disp
from telebot.handlers.user.registration import RegistrationUser


def authorization():
    """Производит аутентификацию бота на основе jwt."""

    try:
        token = auth_with_token()
        return token
    except ValueError as wrong_user_data:
        bot_logger.exception(wrong_user_data)


@disp.message_handler(state=RegistrationUser.request)
async def process_request_registration_user(message: types.Message, state: FSMContext):
    """Добавление нового пользователя в БД на основе API."""
    async with state.proxy() as data:
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
            data = ujson.loads(response.content)
            bot_logger.info(f"[+] Зарегистрирован новый пользователь. ID: {data['id']}, TG: {data['telegram_id']}, PNONE: {data['phone_number']}")

            url = URL + "api/clients/"
            payload = ujson.dumps({"user": data['phone_number'], "client_type": "Обычный клиент"})
            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 201 and response.content:
                bot_logger.info(f"[+] Статус пользователя {data['phone_number']} изменен на 'Обычный клиент'")
                msg = "<i>Регистрация успешно завершена!</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
            
            else:
                bot_logger.info(f"[-] Попытка изменить статус нового пользователя {data['phone_number']} оказалась безуспешной.")
                msg = f"<code>Регистрация прервана! Обратитесь к администратору #admin_phone_number.</code>"  # TODO: добавить номер или ссылку админа в env
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        
        else:
            bot_logger.info(f"[-] Попытка зарегистрировать нового пользователя {data['phone_number']} оказалась безуспешной.")
            msg = f"<code>Регистрация прервана! Обратитесь к администратору #admin_phone_number.</code>"  # TODO: обьединить вызов ошибки
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(commands=['visits'])
async def show_visits(message: types.Message):
    """Отображание всех посещений."""

    bot_logger.info(f"[?] Обработка события: {message}")

    token = authorization()

    url = URL + "api/visits/"
    payload = {}
    headers = {'Authorization': token}
    response = requests.request("GET", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}]. Содержимое: [{response.text}].")
    if response.status_code == 200 and response.content:
        data = ujson.loads(response.content)
        await message.answer(text=f"Ok, данные получены {data}!")
