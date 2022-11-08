from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsAdminFilter(BoundFilter):
    key = 'is_admin'

    async def check(self, message: types.Message) -> bool:
        return message.from_id == 958439388
