from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from logger import bot_logger
from telebot.bot import add_user


# создаём форму и указываем поля
class Form(StatesGroup):
    phone_number = State()
    email = State()
    password = State()
    last_name = State()
    first_name = State()
    is_client = State()


# Начинаем наш диалог
# @di.message_handler(commands=['add_user'])
async def cmd_start(message: types.Message):
    await Form.phone_number.set()
    await message.reply("Введите номер телефона пользователя..")


# Добавляем возможность отмены, если пользователь передумал заполнять
# @dp.message_handler(state='*', commands='cancel')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
# async def cancel_handler(message: types.Message, state: FSMContext):
#     current_state = await state.get_state()
#     if current_state is None:
#         return

#     await state.finish()
#     await message.reply('ОК')


# Сюда приходит ответ с номером телефона
# @dp.message_handler(state=Form.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

    await Form.next()
    await message.reply("Введите email пользователя..")


# Сюда приходит ответ с email
# @dp.message_handler(state=Form.email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text

    await Form.next()
    await message.reply("Введите пароль пользователя..")


# Сюда приходит ответ с паролем
# @dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

    await Form.next()
    await message.reply("Введите фамилию пользователя..")


# Сюда приходит ответ с фамилией
# @dp.message_handler(state=Form.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text

    await Form.next()
    await message.reply("Введите имя пользователя..")


# Сюда приходит ответ с именем
# @dp.message_handler(state=Form.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text

    await Form.next()
    await message.reply("Данный пользователь является клиентом?")


# Сюда приходит ответ с статусом клиента
# @dp.message_handler(state=Form.is_client)
async def process_is_client(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['is_client'] = True
        bot_logger.debug(f"Data: [{data}]")
        add_user(data=data)

    await state.finish()
