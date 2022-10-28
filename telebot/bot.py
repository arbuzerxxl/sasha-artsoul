import asyncio
import ujson
import requests
from aiogram import Bot, Dispatcher, types
from settings import BOT_TOKEN
from auth import auth_with_token


async def show_visits(event: types.Message):

    token = auth_with_token()
    url = "http://127.0.0.1:8000/api/visits/"

    payload = {}
    headers = {'Authorization': token}
    response = requests.request("GET", url, headers=headers, data=payload)

    data = ujson.loads(response.content)
    print(data)

    await event.answer(
        f"Ok, {event.from_user.get_mention(as_html=True)}, данные получены!",
        parse_mode=types.ParseMode.HTML,
    )


async def start_handler(event: types.Message):
    await event.answer(
        f"Привет, {event.from_user.get_mention(as_html=True)} ?!",
        parse_mode=types.ParseMode.HTML,
    )


async def main():
    bot = Bot(token=BOT_TOKEN)
    try:
        disp = Dispatcher(bot=bot)
        disp.register_message_handler(start_handler, commands={"start", "restart"})
        disp.register_message_handler(show_visits, commands={"visits", })
        await disp.start_polling()
    finally:
        await bot.close()

asyncio.run(main())
