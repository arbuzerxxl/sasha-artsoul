from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from telebot.loader import disp, bot
from telebot.keyboards.callbacks import user_callback
from handlers.admin.search_user import SearchUser
from telebot.keyboards.reply_keyboards import continue_cancel_keyboard


class DeleteUser(StatesGroup):
    approve_deletion = State()
    request_delete = State()


@disp.callback_query_handler(user_callback.filter(action="delete"))
async def process_delete_user(query: types.CallbackQuery, state: FSMContext):

    await SearchUser.set_data.set()
    async with state.proxy() as state_data:
        state_data['method'] = 'delete'
    msg = "<i>Вы хотите удалить пользователя, верно?</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=DeleteUser.approve_deletion)
async def process_approve_deletion_user(message: types.Message, state: FSMContext):

    await DeleteUser.next()
    msg = "<i>Уверены, что хотите удалить пользователя?</i>"
    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)
