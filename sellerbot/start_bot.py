from aiogram import executor
from loguru import logger

from src.bot import dp


if __name__ == "__main__":
    logger.add("bot.log", format="{time} {level} {message}", level="TRACE", rotation="10 MB", compression="zip")
    executor.start_polling(dp, skip_updates=True)
