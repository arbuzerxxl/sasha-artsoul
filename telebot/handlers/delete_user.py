import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import disp, bot
from logger import bot_logger
from handlers.utils import authentication
from keyboards.callbacks import user_callback, master_callback, client_callback
from keyboards.reply_keyboards import continue_cancel_keyboard
from keyboards.inline_keyboards import search_user


class DeleteUser(StatesGroup):
    approve_deletion = State()
    request_delete = State()


async def process_delete_set(msg: str, query: types.CallbackQuery) -> types.Message:
    """
    Удаляет предыдущую inline клавиатуру,
    назначает состояние DeleteUser в state_storage и
    перенаправляет в функцию поиска пользователей
    в БД: handlers/search_user.
    """

    await query.message.delete_reply_markup()

    await DeleteUser.approve_deletion.set()

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=search_user)


@disp.callback_query_handler(user_callback.filter(action="delete"))
async def process_delete_user(query: types.CallbackQuery) -> types.Message:
    """
    Принимает запрос пользователя (users:delete).
    Чат-команда быстрого выхода из состояния - /cancel.
    """

    msg = "<i>Вы хотите удалить пользователя, верно?</i>"

    await process_delete_set(msg=msg, query=query)


@disp.callback_query_handler(master_callback.filter(action="delete"))
async def process_delete_master(query: types.CallbackQuery) -> types.Message:
    """То же, что и process_delete_user, но принимает запроспользователя (masters:delete)."""

    msg = "<i>Вы хотите удалить мастера, верно?</i>"

    await process_delete_set(msg=msg, query=query)


@disp.callback_query_handler(client_callback.filter(action="delete"))
async def process_delete_client(query: types.CallbackQuery) -> types.Message:
    """То же, что и process_delete_user, но принимает запроспользователя (clients:delete)."""

    msg = "<i>Вы хотите удалить клиента, верно?</i>"

    await process_delete_set(msg=msg, query=query)


@disp.message_handler(state=DeleteUser.approve_deletion)
async def process_approve_deletion_user(message: types.Message, state: FSMContext) -> types.Message:
    """
    Получает в state {'Петров Петр': {user_response_data}},
    сохраняет необходимые переменные в state для выбранного пользователя,
    выводит сообщение о подтверждении удаления выбранного пользователя.
    """

    await DeleteUser.next()

    async with state.proxy() as state_data:
        state_data['phone_number'] = state_data[message.text]['phone_number']
        state_data['full_name'] = message.text
        state_data['detail_url'] = state_data[message.text]['detail_url']

    msg = "<i>Уверены, что хотите удалить пользователя?</i>"
    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=DeleteUser.request_delete)
async def process_request_delete_user(message: types.Message, state: FSMContext) -> types.Message:
    """Отправляет запрос на удаление пользователя в БД на основе API."""

    async with state.proxy() as state_data:
        user_full_name = state_data.pop('full_name')
        user_phone_number = state_data.pop('phone_number')
        url = state_data['detail_url']

    await state.finish()

    bot_logger.info(f"[?] Обработка события {message.text} от {message.chat.last_name} {message.chat.first_name}")

    token = authentication()

    headers = {'Content-Type': 'application/json', 'Authorization': token}
    response = requests.request("DELETE", url, headers=headers, data=None)
    bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}].")
    if response.status_code == 204:
        msg = "<i>Пользователь успешно удален!</i>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        bot_logger.debug(f"[+] Пользователь удален: {user_full_name}. Телефон: {user_phone_number}.")
    else:
        msg = f"<code>Ошибка при вводе данных. Запрос отклонен: [{response.status_code}]</code>"
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
        bot_logger.debug(f"[!] Пользователь не может быть удален: {user_full_name}. Телефон: {user_phone_number}. Ошибка запроса: {response.status_code}")
