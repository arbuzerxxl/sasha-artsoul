import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from loader import disp, bot
from logger import bot_logger
from settings import URL
from handlers.utils import authentication
from keyboards.callbacks import client_callback, master_callback
from keyboards.reply_keyboards import continue_cancel_keyboard


class CreateUser(StatesGroup):
    set_data = State()
    approve_data = State()
    request_data = State()


@disp.callback_query_handler(client_callback.filter(action="create"))
async def process_create_client(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await CreateUser.set_data.set()
    async with state.proxy() as state_data:
        state_data['is_client'] = True

    msg = text(f"<i>Вы хотите добавить нового клиента, верно?</i>")

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.callback_query_handler(master_callback.filter(action="create"))
async def process_create_master(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await CreateUser.set_data.set()

    async with state.proxy() as state_data:
        state_data['is_client'] = False

    msg = text(f"<i>Вы хотите добавить нового мастера, верно?</i>")

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=CreateUser.set_data)
async def process_create_user(message: types.Message, state: FSMContext):

    await CreateUser.next()

    msg = text(f"<i>Необходимо ввести данные в следующем порядке без запятых:</i>",
               f"<b>Имя Фамилия Номер телефона Пароль</b>",
               f"<i>Пример:</i>",
               f"Иван Иванов 89991112233 ivan2233",
               sep='\n')

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=CreateUser.approve_data)
async def process_create_user(message: types.Message, state: FSMContext):
    response = message.text.split(" ")
    async with state.proxy() as state_data:
        state_data['first_name'] = response[0]
        state_data['last_name'] = response[1]
        state_data['phone_number'] = response[2]
        state_data['password'] = response[3]
        await CreateUser.next()
        msg = text(f"<i>Все данные верны?</i>",
                   f"<b>Имя: </b> {state_data['first_name']}",
                   f"<b>Фамилия: </b> {state_data['last_name']}",
                   f"<b>Номер телефона: </b> {state_data['phone_number']}",
                   f"<b>Пароль: </b> <span class='tg-spoiler'>{state_data['password']}</span>",
                   sep='\n')
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=CreateUser.request_data)
async def process_request_create_user(message: types.Message, state: FSMContext):
    """Добавление нового пользователя в БД на основе API."""

    bot_logger.info(f"[?] Обработка события {message.text} от {message.chat.last_name} {message.chat.first_name}")

    async with state.proxy():

        state_data = await state.get_data()

    await state.finish()

    token = authentication()
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
        msg = f"<code>Ошибка при вводе данных. Запрос отклонен: [{response.status_code}]</code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

        for error in response_data.values():
            msg = f"<b>{error[0]}</b>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
