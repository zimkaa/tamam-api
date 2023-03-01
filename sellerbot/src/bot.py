import logging
import os
from pathlib import Path

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.types.inline_keyboard import InlineKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardButton

from src.logic import write_verification_result
from src.insert_by_sqlalchemy import message_write
from src.settings import TG_TOKEN


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)

my_user_db = {248598498: "Ник", 122274317: "Alex", 277594923: "Anton"}
IMAGE_NAME = "tamam_bot.png"
PROJECT_PATH = Path(__file__).parent.resolve()
IMAGE_PATH = os.path.join(PROJECT_PATH, "img", IMAGE_NAME)


@dp.message_handler(commands=["start"])
async def send_start(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    if message.from_user.id not in my_user_db:
        part1 = f"Извините, {message.from_user.username}, бот вас не знает.\n"
        part2 = str(message.from_user.id)
        text = part1 + part2
        await message.answer(text)
        return None
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("Сайт Tamam.games", url="https://tamam.games")
    markup.add(button1)
    text = "Привет, {0.first_name}! Нажми на кнопку и перейди на сайт)".format(message.from_user)
    await message.answer(
        text,
        reply_markup=markup,
    )


@dp.message_handler(commands=["help"])
async def send_help(message: types.Message):
    """
    This handler will be called when user sends `/help` command
    """
    text = "/help - подсказка\nСтрого следуйте формату запросов, не используйте лишние пробелы и переводы строк!"
    await message.answer(text)


@dp.message_handler(commands=["pic"])
async def send_pic(message: types.Message):
    """
    This handler will be called when user sends `/pic` command
    """
    if os.path.isfile(IMAGE_PATH):
        with open(IMAGE_PATH, "rb") as img:
            await message.answer_photo(img)
    else:
        await message.answer("Техническая неполадка, попробуйте позже")


@dp.message_handler(commands=["getcode"])
async def send_getcode(message: types.Message):
    """
    This handler will be called when user sends `/getcode` command
    """
    if message.from_user.id in my_user_db:
        arguments = message.get_args()
        amount = int(arguments.strip())
        answer = await write_verification_result(amount)
        text = [element.card_code for element in answer]
        text_messages = "\n".join(text)
        await message.answer(text_messages)
    else:
        await message.answer("Ты не админ")


@dp.message_handler(commands=["addcode"])
async def send_addcode(message: types.Message):
    """
    This handler will be called when user sends `/addcode` command
    """
    if message.from_user.id in my_user_db:
        arguments = message.get_args()

        list_arguments = arguments.split("\n")
        text = message_write(list_arguments)
        if text:
            test_message = f"Find {len(list_arguments)} codes \n" + text
            await message.answer(test_message)
        else:
            await message.answer(f"All done. Was upload all={len(list_arguments)} codes")
    else:
        await message.answer("Ты не админ")
