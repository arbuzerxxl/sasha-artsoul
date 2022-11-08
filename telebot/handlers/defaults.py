from aiogram import types
from aiogram.utils.markdown import text, bold, italic, spoiler
from telebot.loader import disp
from telebot.logger import bot_logger
from telebot.filters import IsAdminFilter
from telebot.keyboards.admin_menu import keyboard


@disp.message_handler(commands=["hello"])
async def hello(event: types.Message):

    bot_logger.info(f"[?] Бот обрабатывает событие {event}")

    await event.answer(
        f"Привет, {event.from_user.get_mention(as_html=True)} ?!",
        parse_mode=types.ParseMode.HTML,
    )


@disp.message_handler(commands=["start, restart"])
async def start_handler(event: types.Message):

    bot_logger.info(f"[?] Бот обрабатывает событие {event}")

    await event.answer(
        f"Привет, {event.from_user.get_mention(as_html=True)} ?!",
        parse_mode=types.ParseMode.HTML,
    )


@disp.message_handler(commands=['rm'])
async def process_rm_command(message: types.Message):
    await message.answer("Убираем шаблоны сообщений", reply_markup=types.ReplyKeyboardRemove())


@disp.message_handler(IsAdminFilter(), commands=['admin'])
async def process_menu_command(message: types.Message):
    await message.answer("Здесь отображаются только админ-команды",
                         reply_markup=keyboard)
