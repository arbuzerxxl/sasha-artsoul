from aiogram.utils.callback_data import CallbackData

# --example--

# HANDLERS
# @disp.callback_query_handler(add_user_callback.filter())
# async def show_visits(query: types.CallbackQuery):
#     pass

# CALLBACKS
user_callback = CallbackData("user", "action")

# KEYBOARDS
# keyboard = InlineKeyboardMarkup()
# keyboard.add(InlineKeyboardButton('Добавить клиента', callback_data="add_user"))
