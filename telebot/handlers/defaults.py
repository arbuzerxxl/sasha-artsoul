import prettytable as pt
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram_calendar import SimpleCalendar, DialogCalendar
from aiogram.types import InputMediaPhoto
from aiogram.utils.markdown import text
from loader import disp, bot
from logger import bot_logger
from filters import IsAdminFilter, IsClientFilter
from keyboards.inline_keyboards import visit, admin, menu, user, client, master, calendar, schedule, registration
from keyboards.callbacks import admin_callback, user_callback, calendar_callback, schedule_callback, cancel_callback
from keyboards.reply_keyboards import check_phone_number_keyboard
from handlers.utils import sender_to_admin


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


@disp.message_handler(IsClientFilter(), commands=['rm'])
async def process_rm_command(message: types.Message):

    await message.answer("Убираем шаблоны сообщений", reply_markup=types.ReplyKeyboardRemove())


@disp.message_handler(commands=("start", "restart", ))
async def start_handler(event: types.Message):

    bot_logger.info(f"[?] Обработка события {event.text} от {event.chat.last_name} {event.chat.first_name}")

    await event.answer(
        f"Привет, {event.from_user.get_mention(as_html=True)} ?!",
        parse_mode=types.ParseMode.HTML,
        reply_markup=registration
    )


@disp.message_handler(IsClientFilter(), commands="menu")
async def client_menu_handler(event: types.Message):

    bot_logger.info(f"[?] Обработка события {event.text} от {event.chat.last_name} {event.chat.first_name}")

    msg = "<i>Выберите опцию из предложенного списка</i>"

    await event.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=menu)


@disp.message_handler(commands=['location'])
async def process_geo_location(message: types.Message):

    await bot.send_location(chat_id=message.chat.id, latitude=float(55.797568), longitude=float(37.939155))


@disp.message_handler(commands=['examples'])
async def process_give_examples(message: types.Message):

    data = [InputMediaPhoto("AgACAgIAAxkDAAIQ-GOgPmmahdYuyy9X0CRYhxrLUBm1AAIiwjEbV5IISVWAXsYO14QWAQADAgADdwADLAQ"),
            InputMediaPhoto("AgACAgIAAxkDAAIQ-WOgPmpEIjjQUC4f9Ma1RQdup8qiAAIjwjEbV5IISfbRnc0PsOp9AQADAgADdwADLAQ"),
            InputMediaPhoto("AgACAgIAAxkDAAIQ-mOgPmzkxixNo6DBoOp86jGzSAItAAIkwjEbV5IISd-C5FpcvLiOAQADAgADdwADLAQ"),
            ]

    await bot.send_media_group(chat_id=message.chat.id, media=data)


@disp.message_handler(commands=['channel'])
async def process_give_channel(message: types.Message):

    msg = "https://t.me/+mjzPIE8pi205NTE6"

    await message.answer(text=msg)


@disp.message_handler(commands=['price'])
async def process_give_price(message: types.Message):

    table = pt.PrettyTable(['Процедура', 'Цена'])
    table.align['Процедура'] = 'l'
    table.align['Цена'] = 'c'

    data = [
        ('Маникюр', 1000),
        ('Маникюр с покрытием', 2000),
        ('Коррекция', 2800),
        ('Наращивание', 3800),
        ('Френч', 2500),
        ('Педикюр', 2600),
        ('Педикюр с покрытием (стопа)', 3000),
        ('Педикюр с покрытием (пальчики)', 2300),
    ]

    for symbol, price in data:
        table.add_row([symbol, f'{price}'])

    msg = f'<pre>{table}</pre>'

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(commands=['feedback'])
async def process_feedback(message: types.Message):

    msg = text("Для обратной связи мне необходим Ваш номер телефона.",
               "Для этого воспользуйтесь безопасной функцией телеграмма.",
               sep="\n")

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=check_phone_number_keyboard)


@disp.message_handler(content_types=types.ContentType.CONTACT)
async def process_user_feedback(message: types.Message):

    msg_to_admin = text(f"Пользователь: {message.contact.first_name} {message.contact.last_name} хочет с Вами связаться.",
                        f"t.me/{message.contact.phone_number}",
                        sep="\n")

    await sender_to_admin(msg=msg_to_admin)


@disp.message_handler(IsAdminFilter(), commands=['admin'])
async def process_admin_command(message: types.Message):

    await message.answer("Здесь отображаются только админ-команды",
                         reply_markup=admin)


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
async def process_admin_to_visits(query: types.CallbackQuery):

    await query.message.delete_reply_markup()

    msg = "<i>Вы можете добавить, изменить или удалить запись</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=visit)
