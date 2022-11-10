from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from telebot.loader import disp, bot
from telebot.keyboards.callbacks import user_callback
from telebot.handlers.defaults import cancel_handler
from telebot.keyboards.default import keyboard


class EditUser(StatesGroup):
    find = State()
    check = State()
    set_data = State()
    request = State()


@disp.callback_query_handler(user_callback.filter(action="edit"))
async def process_create_user(query: types.CallbackQuery):

    await EditUser.find.set()

    msg = text("<i>Вы хотите изменить пользователя, верно?</i>")

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)


@disp.message_handler(state=EditUser.find)
async def process_find_create_user(message: types.Message, state: FSMContext):

    if message.text == 'Да':
        await EditUser.next()

        msg = text("<i>Необходимо ввести номер телефона для поиска пользователя в БД.</i>",
                   "<i>Пример:</i>",
                   "89991112233",
                   sep='\n')

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    else:
        await state.finish()

        msg = text(f"<i>Ок, данные о пользователе не будут занесены в БД.</i>")

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=EditUser.set_data)
async def process_set_data_edit_user(message: types.Message, state: FSMContext):

    if message.text == 'Список':
        await EditUser.next()
        msg = text("<i>Введите новые данные соблюдая порядок ввода данных:</i>",
                   "<b>Имя Фамилия Номер телефона Пароль</b>",
                   "<i>Правильно:</i>",
                   "Иван Иванов 89991112233",
                   "<i>Неправильно:</i>",
                   "Иван 89991112233 Иванов")
        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
    else:
        async with state.proxy() as state_data:
            state_data['user_data_key'] = message.text
            await EditUser.next()
            msg = text(f"<i>Введите новые данные для: {message.text}</i>")
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
