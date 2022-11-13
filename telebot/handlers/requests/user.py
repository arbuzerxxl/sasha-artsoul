import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from telebot.settings import URL
from telebot.handlers.requests.utils import authorization, sender_to_admin
from telebot.logger import bot_logger
from telebot.loader import disp
from telebot.handlers.user.registration import RegistrationUser


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
        bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}]. Содержимое: {response.text}.")
        response_data = ujson.loads(response.content)
        if response.status_code == 201 and response.content:
            bot_logger.info(
                f"[+] Зарегистрирован новый пользователь. ID: {response_data['id']}, TG: {response_data['telegram_id']}, PNONE: {response_data['phone_number']}"
            )
            url = URL + "api/clients/"
            payload = ujson.dumps({"user": response_data['phone_number'], "user_type": "Обычный клиент"})
            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 201 and response.content:
                bot_logger.info(f"[+] Статус пользователя {response_data['phone_number']} изменен на 'Обычный клиент'")
                msg = "<i>Регистрация успешно завершена!</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

                admin_msg = f"Пользователь: t.me/+7{response_data['phone_number'][1:]} успешно зарегистрировался."
                await sender_to_admin(msg=admin_msg)

            else:
                bot_logger.info(f"[-] Попытка изменить статус нового пользователя {response_data['phone_number']} оказалась безуспешной.")
                msg = f"<i>Регистрация прервана! Наш администратор в скором времени свяжется с Вами для решения проблемы.</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

                admin_msg = f"Пользователь: t.me/+7{response_data['phone_number'][1:]} создан, но статус не поменялся"
                await sender_to_admin(msg=admin_msg)

        else:
            bot_logger.debug("[!] Попытка зарегистрировать нового пользователя оказалась безуспешной.")
            msg = "<i>К сожалению регистрация прервана! Наш администратор в скором времени свяжется с Вами для решения проблемы.</i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

            for error in response_data.values():
                msg = f"<b>{error[0]}</b>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

            admin_msg = f"Пользователь: t.me/+7{response_data['phone_number'][1:]} не может зарегистрироваться"
            await sender_to_admin(msg=admin_msg)


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
