import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from loader import disp
from logger import bot_logger
from settings import URL
from handlers.utils import make_request
from keyboards.reply_keyboards import continue_cancel_keyboard


class CreateUser(StatesGroup):
    approve_data = State()
    request_data = State()


@disp.callback_query_handler(lambda c: re.fullmatch(pattern=r'^(clients|masters):create$', string=c.data))
async def process_create_user(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    URLS = {
        'clients': URL + "api/clients/",
        'masters': URL + "api/masters/"
    }

    async with state.proxy() as state_data:
        state_data['url'] = URLS.get(query.data.split(":")[0])
        state_data['user_type'] = 'Первый визит' if query.data.split(":")[0] == 'clients' else 'Топ-мастер'
        state_data['is_staff'] = True if query.data.split(":")[0] == 'masters' else False

    msg = text(f"<i>Необходимо ввести данные в следующем порядке без запятых:</i>",
               f"<b>Имя Фамилия Номер телефона Пароль</b>",
               f"<i>Пример:</i>",
               f"Иван Иванов 89991112233 ivan2233",
               sep='\n')

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    await CreateUser.approve_data.set()


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
                   sep='\n')

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=CreateUser.request_data)
async def process_request_create_user(message: types.Message, state: FSMContext):
    """Добавление нового пользователя в БД на основе API."""

    bot_logger.info(f"[?] Обработка события от {message.chat.last_name} {message.chat.first_name}")

    async with state.proxy() as state_data:

        url = state_data.pop("url")

        user_type = state_data.pop("user_type")

        data = await state.get_data()

    await state.finish()

    response, status = await make_request(method="POST", url=(URL + "api/users/"), data=data)

    if status == 201 and response:

        bot_logger.info(f"[+] Зарегистрирован новый пользователь {response['phone_number']} {response['last_name']} {response['first_name']}")

        msg = text("<i>Зарегистрирован новый пользователь:</i>",
                   f"<b>{response['last_name']} {response['first_name']}</b>",
                   f"<b>{response['phone_number']}</b>",
                   sep='\n')

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

        response, status = await make_request(method="POST", url=url, data={'user': response['phone_number'], 'user_type': user_type})

        if status == 201 and response:

            msg = text(f"<i>Статус пользователя <b>{response['user']}</b></i>",
                       f"<i>изменился на {response['user_type']}</i>",
                       sep='\n')

            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

        else:

            bot_logger.debug(f"[!] Попытка изменить статус пользователя оказалась безуспешной [{status}]")
            msg = f"<code>Попытка изменить статус пользователя оказалась безуспешной [{status}]</code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    elif status >= 400:

        for error in response.values():
            for msg in error:
                text = f"<b>{msg}</b>"
                await message.answer(text=text, parse_mode=types.ParseMode.HTML)

    else:

        bot_logger.debug(f"[!] Попытка зарегистрировать нового пользователя оказалась безуспешной [{status}]")
        msg = f"<code>Попытка зарегистрировать нового пользователя оказалась безуспешной [{status}]<code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
