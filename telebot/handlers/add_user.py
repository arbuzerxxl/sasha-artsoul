from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import text, bold, italic, spoiler
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
async def show_visits(message: types.Message):
    await AddUser.phone_number.set()
    await message.answer(text="Введите номер телефона пользователя..")


@disp.message_handler(state='*', commands='cancel')
@disp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer(text='Вы отменили ввод данных. Операция прекращена.')


@disp.message_handler(state=AddUser.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

    await AddUser.next()
    await message.answer(text="Введите email пользователя..")


@disp.message_handler(state=AddUser.email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text

    await AddUser.next()
    await message.answer(text="Введите пароль пользователя..")


@disp.message_handler(state=AddUser.password)
async def process_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text

    await AddUser.next()
    await message.answer(text="Введите фамилию пользователя..")


@disp.message_handler(state=AddUser.last_name)
async def process_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text

    await AddUser.next()
    await message.answer(text="Введите имя пользователя..")


@disp.message_handler(state=AddUser.first_name)
async def process_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text

    await AddUser.next()
    await message.answer(text="Данный пользователь является клиентом?", reply_markup=keyboard)


@disp.message_handler(state=AddUser.is_client)
async def process_is_client(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Да':
            data['is_client'] = True
        else:
            data['is_client'] = False
        await AddUser.next()
        pwd = spoiler(data['password'])
        msg = text(italic("Вы уверены, что необходимо добавить пользователя?"),
                   bold("Имя: ") + f"{data['first_name']}",
                   bold("Фамилия: ") + f"{data['last_name']}",
                   bold("Номер телефона: ") + f"{data['phone_number']}",
                   bold("Email: ") + f"{data['email']}",
                   bold("Пароль: ") + f"{pwd}",
                   bold("Клиент: ") + f"{'Да' if data['is_client'] else 'Нет'}",
                   sep='\n')
        await message.answer(text=msg, parse_mode=types.ParseMode.MARKDOWN_V2, reply_markup=keyboard)
