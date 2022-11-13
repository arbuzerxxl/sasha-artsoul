from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from telebot.loader import disp


class SearchUser(StatesGroup):
    set_data = State()
    check = State()


@disp.message_handler(state=SearchUser.set_data)
async def process_find_create_user(message: types.Message, state: FSMContext):

    await SearchUser.next()

    msg = text("<i>Необходимо ввести номер телефона для поиска пользователя в БД.</i>",
               "<i>Пример: <b>89991112233</b></i>",
               sep='\n')

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
