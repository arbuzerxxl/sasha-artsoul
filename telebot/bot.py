from logger import bot_logger, configure_logging


async def on_startup(dp):
    bot_logger.info("..Bot started..")


async def on_shutdown(dp):
    bot_logger.info("..Bot shutdown..")
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    from aiogram import executor
    from handlers import disp
    configure_logging()
    executor.start_polling(dispatcher=disp, on_startup=on_startup, on_shutdown=on_shutdown, )
