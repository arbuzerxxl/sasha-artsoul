from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from telebot.loader import disp, bot
from telebot.keyboards.callbacks import user_callback
from telebot.handlers.defaults import cancel_handler
from telebot.keyboards.default import keyboard


class CreateUser(StatesGroup):
    set_data = State()
    approve = State()
    request = State()


@disp.callback_query_handler(user_callback.filter(action="create"))
async def process_create_user(query: types.CallbackQuery):

    await CreateUser.set_data.set()

    msg = text(f"<i>Вы хотите добавить нового пользователя, верно?</i>")

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)


@disp.message_handler(state=CreateUser.set_data)
async def process_create_user(message: types.Message, state: FSMContext):

    if message.text == 'Да':
        await CreateUser.next()

        msg = text(f"<i>Необходимо ввести данные в следующем порядке без запятых:</i>",
                   f"<b>Имя Фамилия Номер телефона Пароль</b>",
                   f"<i>Пример:</i>",
                   f"Иван Иванов 89991112233 ivan2233",
                   sep='\n')

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    else:

        await state.finish()

        msg = text(f"<i>Ок, данные о пользователе не будут занесены в БД.</i>")

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=CreateUser.approve)
async def process_create_user(message: types.Message, state: FSMContext):
    response = message.text.split(" ")
    async with state.proxy() as data:
        data['first_name'] = response[0]
        data['last_name'] = response[1]
        data['phone_number'] = response[2]
        data['password'] = response[3]
        data['is_client'] = True
        await CreateUser.next()
        msg = text(f"<i>Все данные верны?</i>",
                   f"<b>Имя: </b> {data['first_name']}",
                   f"<b>Фамилия: </b> {data['last_name']}",
                   f"<b>Номер телефона: </b> {data['phone_number']}",
                   f"<b>Пароль: </b> <span class='tg-spoiler'>{data['password']}</span>",
                   sep='\n')
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)
