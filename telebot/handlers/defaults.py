from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram_calendar import SimpleCalendar, DialogCalendar
from telebot.loader import disp, bot
from telebot.logger import bot_logger
from telebot.filters import IsAdminFilter
from telebot.keyboards.inline_keyboards import visit, menu, user, client, master, calendar, schedule, search_user
from telebot.keyboards.callbacks import admin_callback, user_callback, calendar_callback, schedule_callback, cancel_callback


@disp.message_handler(state='*', commands='cancel')
@disp.message_handler(Text(equals='Отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):

    current_state = await state.get_state()

    if current_state is None:
        return

    await state.finish()
    await message.answer(text='Вы отменили ввод данных. Операция прекращена.')


@disp.callback_query_handler(cancel_callback.filter(action="cancel"), state='*')
async def cancel_handler(query: types.CallbackQuery, state: FSMContext):

    current_state = await state.get_state()

    if current_state is None:
        return

    await state.finish()
    await query.message.answer(text='Вы отменили ввод данных. Операция прекращена.')


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


@disp.message_handler(IsAdminFilter(), commands=['search_user'])
async def process_search_user_command(message: types.Message):

    await message.answer("Поиск пользователей",
                         reply_markup=search_user)


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


@disp.callback_query_handler(admin_callback.filter(action="users"))
async def process_admin_to_user(query: types.CallbackQuery):

    await query.message.delete_reply_markup()

    msg = "<i>Выберите группу</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=user)


@disp.callback_query_handler(user_callback.filter(action="clients"))
async def process_user_to_client(query: types.CallbackQuery):
    
    await query.message.delete_reply_markup()
    
    msg = "<i>Вы можете добавить, изменить или удалить клиента</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=client)


@disp.callback_query_handler(user_callback.filter(action="masters"))
async def process_user_to_master(query: types.CallbackQuery):

    await query.message.delete_reply_markup()
    msg = "<i>Вы можете добавить, изменить или удалить мастера</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=master)


@disp.callback_query_handler(admin_callback.filter(action="schedule"))
async def process_admin_to_calendar(query: types.CallbackQuery):

    await query.message.delete_reply_markup()

    msg = "<i>Выберите действие</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=schedule)


@disp.callback_query_handler(schedule_callback.filter(action="create"))
async def process_schedule_create(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    async with state.proxy() as state_data:
        state_data['method'] = 'create_schedule'
        msg = "<i>Выберите календарь для назначения даты</i>"

        await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML,
                               reply_markup=calendar)


@disp.callback_query_handler(schedule_callback.filter(action="delete"))
async def process_schedule_delete(query: types.CallbackQuery, state: FSMContext):
    await query.message.delete_reply_markup()

    async with state.proxy() as state_data:
        state_data['method'] = 'delete_schedule'
        msg = "<i>Выберите календарь для назначения даты</i>"

        await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML,
                               reply_markup=calendar)


@disp.callback_query_handler(calendar_callback.filter(action="navigation"))
async def process_navigation_calendar(query: types.CallbackQuery):

    await query.message.delete_reply_markup()
    msg = "<i>Выберите дату</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML,
                           reply_markup=await SimpleCalendar().start_calendar())


@disp.callback_query_handler(calendar_callback.filter(action="dialog"))
async def process_dialog_calendar(query: types.CallbackQuery):

    await query.message.delete_reply_markup()

    msg = "<i>Выберите дату</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML,
                           reply_markup=await DialogCalendar().start_calendar())


@disp.callback_query_handler(admin_callback.filter(action="visits"))
async def process_admin_to_calendar(query: types.CallbackQuery):

    msg = "<i></i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=calendar)
