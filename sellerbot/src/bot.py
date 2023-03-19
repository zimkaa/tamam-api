import logging
import os
from pathlib import Path

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.types.inline_keyboard import InlineKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from loguru import logger

from src.logic import write_verification_result
from src.logic import message_write
from src.logic import get_text_not_used_code
from src.settings import TG_TOKEN


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher(bot)

my_user_db = {
    248598498: "Ник",
    122274317: "Alex",
    277594923: "Anton",
}
IMAGE_NAME = "tamam_bot_03.jpg"
PROJECT_PATH = Path(__file__).parent.parent.resolve()
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
    markup = InlineKeyboardMarkup()  # Допустимые команды: resize_keyboard=True
    button1 = InlineKeyboardButton(
        "Отзывы",
        url="https://www.avito.ru/sankt-peterburg/predlozheniya_uslug/popolnenie_oldubil_ozan_papara_paramtl_2732429303#open-reviews-list",
    )
    button2 = InlineKeyboardButton("Сайт Tamam.Games", url="https://tamam.games")
    button3 = InlineKeyboardButton("Помощь", url="@t.me/tamamgames")
    # Вот так создается запрос из кнопки в callback функцию, т.е. вызов минуя команду message_handler(commands="cmd")
    # button4 = InlineKeyboardButton("Купить Steam-Код", callback_data = 'steamcodebuy')
    button4 = InlineKeyboardButton("Купить SteamКод 20TL", callback_data="steamcodebuy20")
    button5 = InlineKeyboardButton("Купить SteamКод 50TL", callback_data="steamcodebuy50")
    button6 = InlineKeyboardButton("Купить SteamКод 100TL", callback_data="steamcodebuy100")

    # markup.add(button1)
    # markup.add(button2)
    # markup.add(button3)
    # markup.add(button4)

    markup.row(button1, button2)
    markup.row(button3)
    markup.add(button4).add(button5).add(button6)

    # text = "Привет, {0.first_name}! Нажми на кнопку и перейди на сайт)".format(message.from_user)
    text = "Добро пожаловать в бота компании <b>Tamam.Games</b>! \n\nС помощью этого бота Вы сможете купить игровые коды Steam в турецких лирах (TL).\nМы работаем без посредников, поэтому у нас лучшие цены на игровые коды Steam!"
    text4Buttons = "Выберите нужное действие:"

    if os.path.isfile(IMAGE_PATH):
        with open(IMAGE_PATH, "rb") as img:
            await message.answer_photo(img, caption=text, parse_mode="HTML", reply_markup=markup)
    # await message.answer(
    #    text4Buttons,
    #    reply_markup=markup,
    # )


# @dp.callback_query_handler(text_contains='steamcodebuy')
# async def steamcodebuy(callback: types.CallbackQuery):
# await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text= "Ты вернулся В главное меню. Жми опять кнопки", parse_mode='Markdown')
# в общем этот тип сообщения кидает сообщение не в чат, а просто на экране в ТГ временное сообщение появляется и исчезает, это не то что мне нужно
# await message.answer("На какое количество лир вы хотите купить Steam кодов(введите число кратное 20)")


@dp.callback_query_handler(Text("steamcodebuy20"))
async def steamcodebuy20(callback: types.CallbackQuery):
    await callback.answer("Код на 20TL")


@dp.callback_query_handler(Text("steamcodebuy50"))
async def steamcodebuy50(callback: types.CallbackQuery):
    await callback.answer("Код на 50TL")


@dp.callback_query_handler(Text("steamcodebuy100"))
async def steamcodebuy100(callback: types.CallbackQuery):
    await callback.answer("Код на 100TL")


@dp.message_handler(commands=["help"])
async def send_help(message: types.Message):
    """
    This handler will be called when user sends `/help` command
    """
    text = "/help - подсказка\nСтрого следуйте формату запросов, не используйте лишние пробелы и переводы строк!"
    await message.answer(text)


@dp.message_handler(commands=["getempty"])
async def send_empty(message: types.Message):
    """
    This handler will be called when user sends `/getempty` command
    """
    text = await get_text_not_used_code()
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
        logger.critical(f"{IMAGE_PATH=}")
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
        logger.critical(f"{list_arguments=}")
        text = await message_write(list_arguments)
        logger.critical(f"{text=}")
        if text:
            test_message = f"Find {len(list_arguments)} codes \n" + text
            await message.answer(test_message)
        else:
            await message.answer(f"All done. Was upload all={len(list_arguments)} codes")
    else:
        await message.answer("Ты не админ")
