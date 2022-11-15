from aiogram.utils.callback_data import CallbackData

admin_callback = CallbackData("menu", "action")

user_callback = CallbackData("users", "action")

client_callback = CallbackData("clients", "action")

master_callback = CallbackData("masters", "action")

calendar_callback = CallbackData("calendars", "action")

schedule_callback = CallbackData("schedule", "action")

visit_callback = CallbackData("visits", "action")

cancel_callback = CallbackData("cancel", "action")

calendar_callback = CallbackData('simple_calendar', 'act', 'year', 'month', 'day')
