from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from telebot.loader import disp
from telebot.keyboards.default import keyboard


class AddUser(StatesGroup):
    phone_number = State()
    email = State()
    password = State()
    last_name = State()
    first_name = State()
    is_client = State()
    request = State()


@disp.message_handler(commands=['add_user'])
async def start_add_user(message: types.Message):
    await AddUser.phone_number.set()
    await message.answer("Введите номер телефона пользователя..")


@disp.message_handler(state='*', commands='cancel')
@disp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer('Вы отменинили ввод данных. Операция прекращена.')


@disp.message_handler(state=AddUser.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

    await AddUser.next()
    await message.answer("Введите email пользователя..")


@disp.message_handler(state=AddUser.email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text

    await AddUser.next()
    await message.answer("Введите пароль пользователя..")


@disp.message_handler(state=AddUser.password)
async def process_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

    await AddUser.next()
    await message.answer("Введите фамилию пользователя..")


@disp.message_handler(state=AddUser.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text

    await AddUser.next()
    await message.answer("Введите имя пользователя..")


@disp.message_handler(state=AddUser.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text

    await AddUser.next()
    await message.answer("Данный пользователь является клиентом?", reply_markup=keyboard)


@disp.message_handler(state=AddUser.is_client)
async def process_is_client(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Да':
            data['is_client'] = True
        else:
            data['is_client'] = False
        await AddUser.next()
        await message.answer(f"Вы уверены, что необходимо добавить пользователя?\n"
                             f"Имя: {data['first_name']}\n"
                             f"Фамилия: {data['last_name']}", reply_markup=keyboard)
