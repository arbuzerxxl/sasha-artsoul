import ujson
import requests
from aiogram import types
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)
from aiogram.dispatcher import FSMContext
from telebot.settings import URL
from telebot.handlers.requests.utils import authorization
from telebot.logger import bot_logger
from telebot.loader import disp
from telebot.handlers.admin import search_user, create_user, edit_user, delete_user, schedule
from telebot.keyboards.reply_keyboards import continue_cancel_keyboard

API_FORM_KEYS = {
    'Имя': 'first_name',
    'Фамилия': 'last_name',
    'Номер телефона': 'phone_number',
    'Пароль': 'password'
}


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
                msg = ("<code>Пользователь не существует! Попробуйте еще раз, вызвав меню админа повторно.</code>")
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
            elif len(response_data) > 1:
                bot_logger.debug(
                    f"[!] Найдено несколько пользователей по номеру {response_data[0]['phone_number']}, id: {[item['id'] for item in response_data]}"
                )
                await state.finish()
                msg = "<code>Было найдено несколько пользователей!</code>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
            else:
                state_data['user_id'] = response_data[0]['id']
                state_data['phone_number'] = response_data[0]['phone_number']
                state_data['is_client'] = response_data[0]['is_client']
                msg = f"<i>Пользователь <b>{response_data[0]['first_name']} {response_data[0]['last_name']}</b> найден.</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)

        else:
            await state.finish()
            msg = f"<code>Сбой в поиске пользователя! Ошибка: [{response.status_code}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=create_user.CreateUser.request_data)
async def process_request_create_user(message: types.Message, state: FSMContext):
    """Добавление нового пользователя в БД на основе API."""

    bot_logger.info(f"[?] Обработка события: {message}")

    async with state.proxy():

        state_data = await state.get_data()

    await state.finish()

    token = authorization()
    url = URL + "api/users/"
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    payload = ujson.dumps(state_data)
    response = requests.request("POST", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}]. Содержимое: [{response.text}].")
    response_data = ujson.loads(response.content)

    if response.status_code == 201 and response.content:
        bot_logger.info(
            f"[+] Зарегистрирован новый пользователь. ID: {response_data['id']}, TG: {response_data['telegram_id']}, PNONE: {response_data['phone_number']}"
        )

        data = {"user": response_data['phone_number']}

        if state_data["is_client"]:
            url = URL + "api/clients/"
            data["user_type"] = "Обычный клиент"
        else:
            url = URL + "api/masters/"
            data["user_type"] = "Топ-мастер"

        payload = ujson.dumps(data)
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 201 and response.content:
            bot_logger.info(f"[+] Статус пользователя {response_data['phone_number']} изменен на {data['user_type']}")
            msg = "<i>Операция успешно завершена!</i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

        else:
            bot_logger.info(f"[-] Попытка изменить статус нового пользователя {response_data['phone_number']} оказалась безуспешной.")
            msg = "<i>Пользователь был добавлен, но статус не изменен!</i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    else:
        bot_logger.debug("[!] Попытка зарегистрировать нового пользователя оказалась безуспешной.")
        msg = "<code>Создание пользователя прервано!</code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

        for error in response_data.values():
            msg = f"<b>{error[0]}</b>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=edit_user.EditUser.request_user_data)
async def process_request_edit_user(message: types.Message, state: FSMContext):
    """Изменение пользователя в БД на основе API."""

    async with state.proxy() as state_data:

        url = URL + f"api/users/{state_data.pop('user_id')}/"
        user_data_key = API_FORM_KEYS.get(state_data.pop('user_data_key'))
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
        response_data = ujson.loads(response.content)
        bot_logger.debug(f"[+] Пользователь изменен. ID: {response_data['id']}. TG: {response_data.get('telegram_id', None)}.")
    else:
        msg = f"<code>Что-то пошло не так! Ошибка: [{response.status_code}]</code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=edit_user.EditUser.request_check_and_change_status)
async def process_request_check_and_change_status_user(message: types.Message, state: FSMContext):
    """Проверка статуса пользователя (клиент/мастер/none) в БД на основе API."""

    bot_logger.info(f"[?] Обработка события: {message}")

    async with state.proxy() as state_data:

        if state_data["is_client"]:
            url = URL + "api/clients/"
        else:
            url = URL + "api/masters/"
        data = {'user': state_data['phone_number']}

    await state.finish()

    token = authorization()

    headers = {'Content-Type': 'application/json', 'Authorization': token}

    payload = ujson.dumps(data)

    response = requests.request("GET", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")
    if response.status_code == 200 and response.content:
        response_data = ujson.loads(response.content)
        data['user_type'] = message.text
        msg = f"<i>Статус пользователя {data['user']} изменен на <b>{data['user_type']}</b></i>"

        if not response_data:
            edit_user.EditUser.next()
            response = requests.request("POST", url, headers=headers, data=payload)
        else:
            url = response_data[0]['detail_url']
            response = requests.request("PATCH", url, headers=headers, data=payload)

        if response.status_code == 200 and response.content:
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        else:
            msg = f"<code>Невозможно сменить статус для пользователя {data['user']}! Ошибка: [{response.status_code}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
    else:
        msg = f"<code>Невозможно сменить статус для пользователя {data['user']}! Ошибка: [{response.status_code}]</code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=delete_user.DeleteUser.request_delete)
async def process_request_delete_user(message: types.Message, state: FSMContext):
    """Удаление пользователя в БД на основе API."""

    async with state.proxy() as state_data:
        user_id = state_data.pop('user_id')
        user_phone_number = state_data.pop('phone_number')
        url = URL + f"api/users/{user_id}/"
        await state.finish()

    bot_logger.info(f"[?] Обработка события: {message}")

    token = authorization()

    headers = {'Content-Type': 'application/json', 'Authorization': token}
    response = requests.request("DELETE", url, headers=headers, data=None)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")
    if response.status_code == 204:
        msg = "<i>Ок, пользователь успешно удален!</i>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        bot_logger.debug(f"[+] Пользователь удален. ID: {user_id}. Телефон: {user_phone_number}.")
    else:
        msg = f"<code>Что-то пошло не так! Ошибка: [{response.status_code}]</code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        bot_logger.debug(f"[!] Пользователь не может быть удален. ID: {user_id}. Телефон: {user_phone_number}. Ошибка запроса: {response.status_code}")


@disp.message_handler(state=schedule.Schedule.set_master)
async def process_set_master_schedule(message: types.Message, state: FSMContext):
    """Изменяет расписание на основе API
       (создает/удаляет доступные для записи даты)."""

    bot_logger.info(f"[?] Обработка события: {message}")

    token = authorization()

    url = URL + "api/masters/"

    headers = {'Content-Type': 'application/json', 'Authorization': token}

    async with state.proxy() as state_data:

        state_data.setdefault("time", message.text)

        response = requests.request("GET", url, headers=headers, data=None)
        if response.status_code == 200 and response.content:
            response_data = ujson.loads(response.content)
            masters_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            bot_logger.debug(f"Create response: {response_data}")
            for master in response_data:
                master_full_name = f"{master['user']['last_name']} {master['user']['first_name']}"
                state_data[master_full_name] = master['user']['phone_number']
                masters_keyboard.add(KeyboardButton(master_full_name))

            msg = f"<i>Выберите мастера</i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=masters_keyboard)
            await schedule.Schedule.create_request.set()
        else:
            state.finish()
            msg = f"<code>Ошибка: [{response.status_code}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=schedule.Schedule.create_request)
async def process_create_schedule(message: types.Message, state: FSMContext):
    """Создает запись из расписания на основе API"""

    bot_logger.info(f"[?] Обработка события: {message}")

    token = authorization()

    url = URL + "api/calendar/"

    headers = {'Content-Type': 'application/json', 'Authorization': token}

    async with state.proxy() as state_data:

        data = {"date_time": state_data["date"] + " " + state_data["time"], "master": state_data[message.text]}

        payload = ujson.dumps(data)
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 201 and response.content:
            response_data = ujson.loads(response.content)
            msg = f"<i>Запись <b>[{response_data['date_time']}] [{state_data[message.text]}]</b> создана в расписании</i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
            await state.finish()
        else:
            msg = f"<code>Ошибка: [{response.status_code}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=schedule.Schedule.delete_request)
async def process_delete_schedule(message: types.Message, state: FSMContext):
    """Удаляет запись из расписания на основе API"""

    bot_logger.info(f"[?] Обработка события: {message}")

    token = authorization()

    url = URL + "api/calendar/"

    headers = {'Content-Type': 'application/json', 'Authorization': token}

    async with state.proxy() as state_data:

        state_data.setdefault("time", message.text)

        data = {"date_time": state_data["date"] + " " + state_data["time"]}

        payload = ujson.dumps(data)
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200 and response.content:
            response_data = ujson.loads(response.content)
            if not response_data:
                msg = f"<i>Запись <b>[{data['date_time']}]</b> не найдена в расписании</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
                await state.finish()
            else:
                msg = f"<i>Запись <b>[{data['date_time']}]</b> найдена в расписании</i>"
                url = response_data[0]['detail_url']
                response = requests.request("DELETE", url, headers=headers, data=None)
                if response.status_code == 204:
                    msg = f"<i>Запись <b>[{data['date_time']}]</b> успешно удалена из расписания!</i>"
                    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
                    bot_logger.debug(f"[+] Запись <b>[{data['date_time']}]</b> успешно удалена из расписания.")
                else:
                    msg = f"<code>Что-то пошло не так! Ошибка: [{response.status_code}]</code>"
                    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
                    bot_logger.debug(f"[!] Запись <b>[{data['date_time']}]</b> не может быть удалена из расписания. Ошибка запроса: {response.status_code}")
        else:
            msg = f"<code>Ошибка при вводе данных. Запрос отклонен: [{response.status_code}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
