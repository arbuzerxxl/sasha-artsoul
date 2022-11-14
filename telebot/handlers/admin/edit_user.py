from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from telebot.loader import disp, bot
from telebot.keyboards.callbacks import user_callback
from handlers.admin.search_user import SearchUser
from telebot.keyboards.reply_keyboards import continue_cancel_keyboard, user_form_keyboard, client_status_keyboard, master_status_keyboard


class EditUser(StatesGroup):
    select_change = State()
    set_data = State()
    request_user_data = State()
    request_check_and_change_status = State()


@disp.callback_query_handler(user_callback.filter(action="edit"))
async def process_edit_user(query: types.CallbackQuery, state: FSMContext):

    await SearchUser.set_data.set()
    async with state.proxy() as state_data:
        state_data['method'] = 'edit'
    msg = "<i>Вы хотите изменить пользователя, верно?</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=EditUser.select_change)
async def process_select_change_edit_user(message: types.Message):

    await EditUser.next()
    msg = "<i>Что будем менять?</i>"
    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=user_form_keyboard)


@disp.message_handler(state=EditUser.set_data)
async def process_set_data_edit_user(message: types.Message, state: FSMContext):

    if message.text == "Статус":
        await EditUser.request_check_and_change_status.set()
        msg = f"<i>Выберите новый <b>{message.text}</b></i>"
        async with state.proxy() as state_data:
            if state_data["is_client"]:
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=client_status_keyboard)
            else:
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=master_status_keyboard)
    else:
        async with state.proxy() as state_data:
            state_data['user_data_key'] = message.text
            await EditUser.next()
            msg = f"<i>Введите новые данные для: <b>{message.text}</b></i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
