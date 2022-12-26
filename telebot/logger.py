import logging

bot_logger = logging.getLogger('Telebot')


def configure_logging():

    # bot_handler = logging.FileHandler(filename='bot.log', mode='a')
    bot_handler = logging.StreamHandler()
    bot_formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname) -10s %(filename) - 15s %(message)s', datefmt='%d.%m.%Y %H:%M:%S')

    bot_handler.setFormatter(bot_formatter)
    bot_logger.addHandler(bot_handler)

    bot_logger.setLevel(logging.DEBUG)
