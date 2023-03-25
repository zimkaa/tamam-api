from aiogram.utils.executor import start_polling
from aiogram import Dispatcher
from loguru import logger

from src.bot import dp
from src.settings import ADMIN_CHANNEL_ID


ADMIN_ID_LIST = ADMIN_CHANNEL_ID.split(",")


async def start_bot(dispatcher: Dispatcher):
    for admin_user in ADMIN_ID_LIST:
        await dispatcher.bot.send_message(admin_user, text="Bot started")


async def stop_bot(dispatcher: Dispatcher):
    for admin_user in ADMIN_ID_LIST:
        await dispatcher.bot.send_message(admin_user, text="Bot stopped")


def start():
    logger.add("bot.log", format="{time} {level} {message}", level="TRACE", rotation="10 MB", compression="zip")
    start_polling(dp, skip_updates=True, on_startup=start_bot, on_shutdown=stop_bot)


if __name__ == "__main__":
    start()
