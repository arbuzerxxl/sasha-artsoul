import os
from aiogram import types
from settings import URL
from handlers.utils import make_request
from aiogram.dispatcher.filters import BoundFilter


class IsAdminFilter(BoundFilter):
    key = 'is_admin'

    async def check(self, message: types.Message) -> bool:
        return any(int(admin) == message.from_id for admin in os.environ.get("TELEBOT_ID_ADMINS").split(" "))


class IsClientFilter(BoundFilter):
    key = 'is_client'

    async def check(self, message: types.Message) -> bool:

        response, status = await make_request(method="GET", url=(URL + "api/users/"), data={"telegram_id": message.from_id})

        return False if status == 200 and not response else True
