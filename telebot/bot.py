import asyncio
import ujson
import requests
from aiogram import Bot, Dispatcher, types
from settings import BOT_TOKEN, URL
from auth import auth_with_token
from logger import configure_logging, bot_logger


async def show_visits(event: types.Message):

    bot_logger.info(f"[?] Обработка события: {event}")

    try:
        token = auth_with_token()
    except ValueError as wrong_user_data:
        bot_logger.exception(wrong_user_data)

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
    try:
        disp = Dispatcher(bot=bot)
        disp.register_message_handler(start_handler, commands={"start", "restart"})
        disp.register_message_handler(show_visits, commands={"visits"})
        disp.register_message_handler(hello, commands={"hello"})
        await disp.start_polling()
    finally:
        await bot.close()

if __name__ == '__main__':
    configure_logging()
    asyncio.run(main())
