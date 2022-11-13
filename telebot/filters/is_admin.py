import os
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsAdminFilter(BoundFilter):
    key = 'is_admin'

    async def check(self, message: types.Message) -> bool:
        return any(int(admin) == message.from_id for admin in os.environ.get("TELEBOT_ADMINS").split(" "))
