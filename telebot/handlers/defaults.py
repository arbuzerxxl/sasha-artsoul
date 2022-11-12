from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from telebot.loader import disp, bot
from telebot.logger import bot_logger
from telebot.filters import IsAdminFilter
from telebot.keyboards.admin import visit, menu, user
from telebot.keyboards.callbacks import admin_callback


@disp.message_handler(state='*', commands='cancel')
@disp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):

    current_state = await state.get_state()

    if current_state is None:
        return

    await state.finish()
    await message.answer(text='Вы отменили ввод данных. Операция прекращена.')


@disp.message_handler(commands=["hello"])
async def hello(event: types.Message):

    bot_logger.info(f"[?] Бот обрабатывает событие {event}")

    await event.answer(
        f"Привет, {event.from_user.get_mention(as_html=True)} ?!",
        parse_mode=types.ParseMode.HTML,
    )
    # await bot.send_message(text=f"{event.chat.first_name} {event.chat.last_name} поздоровался со мной",
    #                        chat_id=1018379557)


@disp.message_handler(commands=["start, restart"])
async def start_handler(event: types.Message):

    bot_logger.info(f"[?] Бот обрабатывает событие {event}")

    await event.answer(
        f"Привет, {event.from_user.get_mention(as_html=True)} ?!",
        parse_mode=types.ParseMode.HTML,
    )


# @disp.message_handler(content_types=types.ContentType.ANY)
# async def start_handler(event: types.Message):

#     bot_logger.info(f"[?] Бот обрабатывает событие {event}")

#     await event.answer(
#         f"{event.text}",
#         parse_mode=types.ParseMode.MARKDOWN_V2,
#     )


@disp.message_handler(commands=['rm'])
async def process_rm_command(message: types.Message):
    await message.answer("Убираем шаблоны сообщений", reply_markup=types.ReplyKeyboardRemove())


@disp.message_handler(IsAdminFilter(), commands=['admin'])
async def process_admin_command(message: types.Message):
    await message.answer("Здесь отображаются только админ-команды",
                         reply_markup=menu)


@disp.callback_query_handler(admin_callback.filter(action="user"))
async def process_admin_to_user(query: types.CallbackQuery):
    msg = "<i>Вы можете добавить, изменить или удалить пользователя</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=user)
