import asyncio
import ujson
import re
from django.conf import settings
import requests
from aiogram import Bot, Dispatcher, types
import settings


async def start_handler(event: types.Message):
    await event.answer(
        f"Привет, {event.from_user.get_mention(as_html=True)} ?!",
        parse_mode=types.ParseMode.HTML,
    )


async def show_visits(event: types.Message):

    try:
        url = "http://127.0.0.1:8000/api/visits"
        with open('telegram-bot/tokens.txt', 'r') as tk:
            regex_token = r"^BOT_TOKEN='([.]{+})'$"
            for line in tk:
                matched = re.match(line, regex_token)
                token = matched[1]
        payload = {}
        headers = {'Authorization': token}

        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code == 401:
            raise ValueError('Токен недействителен')
        else:
            data = ujson.loads(response.content)
            print(data)

            await event.answer(f"Ok, {event.from_user.get_mention(as_html=True)}, щас глянем",
                               parse_mode=types.ParseMode.HTML,)

    except (ValueError, AttributeError) as exp:
        print(exp)
    
        # url = "http://127.0.0.1:8000/api/token/"

        # payload = ujson.dumps({"phone_number": "89850768512",
        #                        "password": "kss130795"
        #                        })
        # headers = {'Content-Type': 'application/json'}

        # response = requests.request("POST", url, headers=headers, data=payload)

        # with open('settings.py', 'a') as stgs:
        #     stgs.write(f"JWT_ACCESS_TOKEN='{ujson.loads(response.content)['access']}'\n")
        #     stgs.write(f"JWT_REFRESH_TOKEN='{ujson.loads(response.content)['refresh']}'\n")

    await event.answer(
        f"Ok, {event.from_user.get_mention(as_html=True)}, щас глянем",
        parse_mode=types.ParseMode.HTML,
    )


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        disp = Dispatcher(bot=bot)
        disp.register_message_handler(start_handler, commands={"start", "restart"})
        disp.register_message_handler(show_visits, commands={"visits", })
        await disp.start_polling()
    finally:
        await bot.close()

asyncio.run(main())
