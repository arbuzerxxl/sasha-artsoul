from aiogram import Bot, Dispatcher
from settings import BOT_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage

try:
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    disp = Dispatcher(bot=bot, storage=storage)
except Exception as exc:
    print(exc)
