from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from logger import bot_logger
from bot import add_user


# создаём форму и указываем поля
class AddUser(StatesGroup):
    phone_number = State()
    email = State()
    password = State()
    last_name = State()
    first_name = State()
    is_client = State()
    sent = State()


# @di.message_handler(commands=['add_user'])
async def start_add_user(message: types.Message):
    await AddUser.phone_number.set()
    await message.answer("Введите номер телефона пользователя..")


# Добавляем возможность отмены, если пользователь передумал заполнять
# @dp.message_handler(state='*', commands='cancel')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
# async def cancel_handler(message: types.Message, state: FSMContext):
#     current_state = await state.get_state()
#     if current_state is None:
#         return

#     await state.finish()
#     await message.reply('ОК')


# @dp.message_handler(state=Form.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

    await AddUser.next()
    await message.answer("Введите email пользователя..")


# @dp.message_handler(state=Form.email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text

    await AddUser.next()
    await message.answer("Введите пароль пользователя..")


# @dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

    await AddUser.next()
    await message.answer("Введите фамилию пользователя..")


# @dp.message_handler(state=Form.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text

    await AddUser.next()
    await message.reply("Введите имя пользователя..")


# @dp.message_handler(state=Form.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text

    await AddUser.next()
    await message.answer("Данный пользователь является клиентом?")


# @dp.message_handler(state=Form.is_client)
async def process_is_client(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Да':
            data['is_client'] = True
        else:
            data['is_client'] = False
        await message.answer(f"Вы уверены, что необходимо добавить пользователя?\n \
                             Имя: {data['first_name']},\n \
                             Фамилия: {data['last_name']}")
    if message.text == 'Да':  # TODO: не работает
        await AddUser.next()
    else:
        state.finish()
