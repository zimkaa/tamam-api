import csv
import datetime

from loguru import logger

from src.db.dals import CodeDAL
from src.db.models import Card
from src.db.session import async_session
from src.utils.telegram import send_telegram_message


class NoCardError(Exception):
    """No code to give"""

    pass


class WriteToDBError(Exception):
    """Trouble with writing in DB"""

    pass


def _make_change(amount: int, card_rows: list[tuple[Card]]) -> list[Card] | int:
    logger.info("_make_change")
    # TODO должен в порядке убывания
    denominations: dict[int, list[Card]] = dict()
    card_list = list()
    for card in card_rows:
        if denominations.get(card[0].amount):
            denominations[card[0].amount] += [card[0]]
        else:
            denominations[card[0].amount] = [card[0]]
    result = {}
    if denominations.get(amount):
        card = denominations.get(amount).pop()
        card_list.append(card)
        return card_list
    if amount == 60 or amount == 80:
        count = int(amount / 20)
        if len_20 := denominations.get(20):
            if len(len_20) >= count:
                for _ in range(count):
                    card = denominations.get(20).pop()
                    card_list.append(card)
        else:
            logger.critical(f"No card to {amount=}")
            # raise NoCardError
            return amount
        return card_list
    for denom in sorted(denominations.keys(), reverse=True):
        while amount >= denom and len(denominations.get(denom, 0)) > 0:
            if denom in result:
                result[denom] += 1
                card = denominations[denom].pop()
                card_list.append(card)
            else:
                result[denom] = 1
                card = denominations[denom].pop()
                card_list.append(card)
            amount -= denom
    logger.critical(f"{type(result)} {result=}")
    logger.critical(f"{type(card_list)} {card_list=}")
    if amount > 0:
        logger.critical(f"No card to {amount=}")
        # raise NoCardError
        return amount
    else:
        return card_list


async def get_text_not_used_code() -> str:
    code_dict = await get_sorted_not_used_code()
    text = [f"{amount}TL = {count}штук" for amount, count in code_dict.items()]
    text_messages = "\n".join(text)
    return text_messages


async def get_sorted_not_used_code() -> dict[int, list[Card]]:
    logger.info("get_sorted_not_used_code")
    db = async_session()
    async with db as session:
        async with session.begin():
            code_dal = CodeDAL(session)

            card_rows = await code_dal.get_valid_code()
            if card_rows is None:
                text = "AHTUNG!!! We don't have any empty code"
                logger.error(text)
                await send_telegram_message(text)

            denominations: dict[int, list[Card]] = dict()
            for card in card_rows:
                if denominations.get(card[0].amount):
                    denominations[card[0].amount] += 1
                else:
                    denominations[card[0].amount] = 1
    return denominations


async def write_verification_result(needed_amount: int) -> list[Card]:
    logger.info("write_verification_result")
    db = async_session()
    async with db as session:
        async with session.begin():
            code_dal = CodeDAL(session)

            card_rows = await code_dal.get_valid_code()
            if card_rows is None:
                text = f"AHTUNG!!! We don't have codes to sell. Customer paid for {needed_amount=}"
                logger.error(text)
                await send_telegram_message(text)
                raise NoCardError

            give_away_list_cards = _make_change(needed_amount, card_rows)
            logger.debug(f"{give_away_list_cards=}")
            if isinstance(give_away_list_cards, int):
                need_buy_amount = needed_amount - give_away_list_cards
                text = (
                    f"AHTUNG!!! We don't have enough codes to sell. Need {needed_amount}TL"
                    f" we don't have codes for the amount {need_buy_amount}TL"
                    f" but we have codes only for {give_away_list_cards}TL"
                )
                logger.error(text)
                await send_telegram_message(text)
                raise NoCardError

            updated_true = await code_dal.update_card_row(give_away_list_cards, 1, "alexander@example.com")
            logger.debug(f"{updated_true=}")
            if not updated_true:
                message_string = ""
                for card in give_away_list_cards:
                    message_string += (
                        f"card_id={card[0].card_id} card_code={card[0].card_code} amount={card[0].amount}\n"
                    )
                message_string += f"Саша получил код time={datetime.datetime.utcnow()}"
                text = f"AHTUNG!!! Can't write to db \n{needed_amount=}\nused chain {message_string}"
                logger.error(text)
                await send_telegram_message(text)
                raise WriteToDBError
            return give_away_list_cards


async def message_write(message: list[str]) -> None | str:
    text = ""
    duplicates_count = 0
    db = async_session()
    async with db as session:
        async with session.begin():
            code_dal = CodeDAL(session)
            reader = csv.reader(message)
            keys = ["card_code", "amount", "amount_tl"]
            for record in reader:
                data_to_write = dict(zip(keys, [record[0], int(record[1]), int(record[2])]))
                new_card = Card(**data_to_write)
                logger.error(f"{type(new_card.amount)} {new_card.amount=}")
                logger.error(f"{type(new_card.amount_tl)} {new_card.amount_tl=}")
                duplicate = await code_dal.check_duplicate(new_card.card_code)
                if duplicate:
                    text += f"{new_card.card_code}\n"
                    duplicates_count += 1
                else:
                    await code_dal.add_new_card(new_card)

    if text:
        start = "Такой/такие уже был добавлен!\n"
        text_send = start + text + f"\nDuplicates count: {duplicates_count}"
        return text_send
