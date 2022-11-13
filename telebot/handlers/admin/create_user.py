from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from telebot.loader import disp, bot
from telebot.keyboards.callbacks import client_callback, master_callback
from telebot.keyboards.default import continue_cancel_keyboard


class CreateUser(StatesGroup):
    set_data = State()
    approve_data = State()
    request_data = State()


@disp.callback_query_handler(client_callback.filter(action="create"))
async def process_create_client(query: types.CallbackQuery, state: FSMContext):

    await CreateUser.set_data.set()
    async with state.proxy() as state_data:
        state_data['is_client'] = True

    msg = text(f"<i>Вы хотите добавить нового клиента, верно?</i>")

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.callback_query_handler(master_callback.filter(action="create"))
async def process_create_master(query: types.CallbackQuery, state: FSMContext):

    await CreateUser.set_data.set()

    async with state.proxy() as state_data:
        state_data['is_client'] = False

    msg = text(f"<i>Вы хотите добавить нового мастера, верно?</i>")

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=CreateUser.set_data)
async def process_create_user(message: types.Message, state: FSMContext):

    await CreateUser.next()

    msg = text(f"<i>Необходимо ввести данные в следующем порядке без запятых:</i>",
               f"<b>Имя Фамилия Номер телефона Пароль</b>",
               f"<i>Пример:</i>",
               f"Иван Иванов 89991112233 ivan2233",
               sep='\n')

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=CreateUser.approve_data)
async def process_create_user(message: types.Message, state: FSMContext):
    response = message.text.split(" ")
    async with state.proxy() as data:
        data['first_name'] = response[0]
        data['last_name'] = response[1]
        data['phone_number'] = response[2]
        data['password'] = response[3]
        await CreateUser.next()
        msg = text(f"<i>Все данные верны?</i>",
                   f"<b>Имя: </b> {data['first_name']}",
                   f"<b>Фамилия: </b> {data['last_name']}",
                   f"<b>Номер телефона: </b> {data['phone_number']}",
                   f"<b>Пароль: </b> <span class='tg-spoiler'>{data['password']}</span>",
                   sep='\n')
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)
