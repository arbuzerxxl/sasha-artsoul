import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import (State, StatesGroup)
from loader import disp, bot
from handlers.utils import make_request
from keyboards.callbacks import schedule_callback
from keyboards.reply_keyboards import continue_cancel_keyboard
from keyboards.inline_keyboards import search_schedule


class ScheduleDelete(StatesGroup):
    approve_deletion = State()
    request_delete = State()


@disp.callback_query_handler(schedule_callback.filter(action="delete"))
async def process_delete_schedule(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await ScheduleDelete.approve_deletion.set()

    msg = "<i>Вы хотите удалить запись из календаря, верно?</i>"

    await bot.send_message(chat_id=query.message.chat.id, text=msg, parse_mode=types.ParseMode.HTML, reply_markup=await search_schedule(method='delete'))


@disp.callback_query_handler(lambda c: re.fullmatch(
    pattern=r'^((0[1-9]{1}|[1-2]{1}[0-9]{1}|3[0-1]{1})-(0[1-9]{1}|1[1-2]{1})-20[\d]{2} [\d]{2}:[\d]{2}#[\w\d\-\/\:]{1,})$',
    string=c.data), state=ScheduleDelete.approve_deletion)
async def process_approve_deletion(query: types.CallbackQuery, state: FSMContext):

    await query.message.delete_reply_markup()

    await ScheduleDelete.next()

    date_time, detail_url = tuple(query.data.split("#"))

    async with state.proxy() as state_data:
        state_data['detail_url'] = detail_url
        state_data['date_time'] = date_time

    msg = f"<i>Уверены, что хотите удалить запись <b>{date_time}</b>?</i>"

    await query.message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=ScheduleDelete.request_delete)
async def process_delete_schedule(message: types.Message, state: FSMContext):
    """Удаляет запись из расписания на основе API"""

    async with state.proxy() as state_data:

        print(state_data['detail_url'])

        status = await make_request(method="DELETE", url=state_data['detail_url'])

        if status == 204:

            msg = f"<b>Запись {state_data['date_time']} успешно удалена из календаря</b>"

        else:
            msg = f"<code>Ошибка: [{status}]</code>"

    await state.finish()

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)
