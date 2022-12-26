import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import disp
from logger import bot_logger
from settings import URL
from handlers.utils import make_request
from keyboards.reply_keyboards import continue_cancel_keyboard
from keyboards.inline_keyboards import search_user


class DeleteUser(StatesGroup):
    approve_deletion = State()
    request = State()


@disp.callback_query_handler(lambda c: re.fullmatch(pattern=r'^(clients|masters):delete$', string=c.data))
async def process_delete_user(query: types.CallbackQuery, state: FSMContext) -> types.Message:
    """Выдает список доступных для удаления клиентов/мастеров"""

    await query.message.delete_reply_markup()

    await DeleteUser.approve_deletion.set()

    msg = f"<i>Необходимо выбрать клиента</i>" if query.data.split(":")[0] == 'clients' else f"<i>Необходимо выбрать мастера</i>"

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=await search_user(user_type=query.data.split(":")[0][0:-1]))


@disp.callback_query_handler(lambda c: re.fullmatch(
    pattern=r'^([\d]{11}#([А-Я]{1}[а-яё]{2,15})\s([А-Я]{1}[а-яё]{2,15}))$',
    string=c.data), state=DeleteUser.approve_deletion)
async def process_approve_deletion_user(query: types.CallbackQuery, state: FSMContext) -> types.Message:
    """Сохраняет данные о выбранном пользователе в состояние"""

    await query.message.delete_reply_markup()

    await DeleteUser.next()

    user_phone, user_name = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        state_data["user_phone"] = user_phone
        state_data["user_name"] = user_name

        response, status = await make_request(method="GET", url=(URL + 'api/users/'), data={'phone_number': state_data['user_phone']})

        state_data['detail_url'] = response[0]['detail_url']

        msg = f"<i>Уверены, что хотите удалить пользователя <b>{state_data['user_name']}</b>?</i>"

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=DeleteUser.request)
async def process_request_delete_user(message: types.Message, state: FSMContext) -> types.Message:
    """Удаляет пользователя посредством API"""

    bot_logger.info(f"[?] Обработка события от {message.chat.last_name} {message.chat.first_name}")

    async with state.proxy() as state_data:

        status = await make_request(method="DELETE", url=state_data['detail_url'])

        if status == 204:

            bot_logger.info(f"[+] Пользователь {state_data['user_name']} успешно удален")

            msg = f"<i>Пользователь <b>{state_data['user_name']}</b> успешно удален</i>"

            await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

        else:

            bot_logger.info(f"[-] Попытка удалить пользователя {state_data['user_name']} оказалась безуспешной [{status}]")
            msg = f"<code>Попытка удалить пользователя <b>{state_data['user_name']}</b> оказалась безуспешной [{status}]<code>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=types.ReplyKeyboardRemove())

    await state.finish()
