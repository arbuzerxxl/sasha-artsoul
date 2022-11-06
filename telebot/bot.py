import asyncio
import ujson
import requests
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telebot.handlers.add_user import *
from aiogram import Bot, Dispatcher, types
from settings import BOT_TOKEN, URL
from auth import auth_with_token
from logger import configure_logging, bot_logger


def authentification():
    """Производит аутентификацию на основе jwt."""

    try:
        token = auth_with_token()
        return token
    except ValueError as wrong_user_data:
        bot_logger.exception(wrong_user_data)


async def show_visits(event: types.Message):
    """Отображание всех посещений."""

    bot_logger.info(f"[?] Обработка события: {event}")

    token = authentification()

    url = URL + "api/visits/"
    payload = {}
    headers = {'Authorization': token}
    response = requests.request("GET", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}]. Содержимое: [{response.content}].")
    if response.status_code == 200 and response.content:
        data = ujson.loads(response.content)
        await event.answer(
            f"Ok, данные получены {data}!",
        )


async def add_user(event: types.Message, state: FSMContext):
    """Добавление нового пользователя в БД на основе API."""

    bot_logger.info(f"[?] Обработка события: {event}")

    token = authentification()

    url = URL + "api/users/"
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    data = await state.get_data()
    payload = ujson.dumps(data)
    await state.finish()
    response = requests.request("POST", url, headers=headers, data=payload)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}]. Содержимое: [{response.content}].")
    if response.status_code == 201 and response.content:
        # data = ujson.loads(response.content)
        await event.answer(f"Ok, пользователь успешно добавлен!")
    else:
        await event.answer(f"Что-то пошло не так! Ошибка: [{response.status_code}]")


async def hello(event: types.Message):

    bot_logger.info(f"[?] Бот обрабатывает событие {event}")

    await event.answer(
        f"Привет, {event.from_user.get_mention(as_html=True)} ?!",
        parse_mode=types.ParseMode.HTML,
    )


async def start_handler(event: types.Message):

    bot_logger.info(f"[?] Бот обрабатывает событие {event}")

    await event.answer(
        f"Привет, {event.from_user.get_mention(as_html=True)} ?!",
        parse_mode=types.ParseMode.HTML,
    )


async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    try:
        disp = Dispatcher(bot=bot, storage=storage)
        disp.register_message_handler(start_handler, commands={"start", "restart"})
        disp.register_message_handler(show_visits, commands={"visits"})
        disp.register_message_handler(hello, commands={"hello"})

        disp.register_message_handler(start_add_user, commands=['add_user'])
        disp.register_message_handler(process_phone_number, state=AddUser.phone_number)
        disp.register_message_handler(process_email, state=AddUser.email)
        disp.register_message_handler(process_password, state=AddUser.password)
        disp.register_message_handler(process_last_name, state=AddUser.last_name)
        disp.register_message_handler(process_first_name, state=AddUser.first_name)
        disp.register_message_handler(process_is_client, state=AddUser.is_client)
        disp.register_message_handler(add_user, state=AddUser.sent)
        await disp.start_polling()
    finally:
        await bot.close()

if __name__ == '__main__':
    configure_logging()
    asyncio.run(main())
