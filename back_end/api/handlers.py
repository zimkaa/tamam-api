import json

from fastapi import APIRouter, Depends, HTTPException, Request

# from starlette.responses import RedirectResponse
# from starlette.status import HTTP_302_FOUND
from starlette.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from loguru import logger

from .models import ResponseDigiseller
from back_end.settings import (
    APP_NAME,
    TEST_CHEK_CODE_URL,
    TEST_DIGISELLER_TOKEN,
    DIGISELLER_TOKEN,
    CHEK_CODE_URL,
)
from back_end.db.dals import CodeDAL
from back_end.db.session import get_db
from back_end.db.models import Card
from back_end.utils.telegramm import send_telegram_message


templates = Jinja2Templates(directory="back_end/templates")
user_router = APIRouter()


async def _create_new_code(code: str, db) -> None:
    """Write to DB code from query

    :param code: code
    :type code: str
    :param db: db connection
    :type db: _type_
    """
    async with db as session:
        async with session.begin():
            code_dal = CodeDAL(session)
            try:
                await code_dal.create_code(code=code)
            except Exception as error:
                text = f"_create_new_code some trouble with writing\n{error=}"
                logger.error(text)
                await send_telegram_message(text)


async def _get_verification_result(code: str) -> ResponseDigiseller:
    """Do request to check number of code

    :param code: number of code
    :type code: str
    :return: answer from Digiseller
    :rtype: ResponseDigiseller
    """
    try:
        async with httpx.AsyncClient() as client:
            # url = CHEK_CODE_URL.format(token=DIGISELLER_TOKEN, unique_code=code)
            url = TEST_CHEK_CODE_URL.format(token=TEST_DIGISELLER_TOKEN, unique_code=code)
            response = await client.get(url)
            logger.critical(f"_check_code {response.text=}")
            digi_answer = json.loads(response.content)
    except Exception as error:
        text = f"_get_verification_result trouble with query to Digiseller {error=}"
        logger.error(text)
        await send_telegram_message(text)
        digi_answer = {}
    return ResponseDigiseller(**digi_answer)


async def _is_received(digi_answer: ResponseDigiseller, db) -> bool:
    """Checks whether this code has already been issued

    :param digi_answer: answer from Digiseller
    :type digi_answer: ResponseDigiseller
    :param db: db connection
    :type db: _type_
    :return: true or false
    :rtype: bool
    """
    async with db as session:
        async with session.begin():
            code_dal = CodeDAL(session)
            exist = await code_dal.check_code_in_db(inv=digi_answer.inv)
            if exist:
                text = f"_is_received code has already been issued {exist=}"
                logger.error(text)
                await send_telegram_message(text)
                return True
    return False


async def _create_certificates_chain(order_amount: float, card_rows: list[tuple[Card]]) -> list[Card] | None:
    """Create chain of codes to give for client
    if amount not covered srnd mrssage to Telegramm

    :param order_amount: _description_
    :type order_amount: float
    :param card_rows: _description_
    :type card_rows: list[tuple[Card]]
    :return: _description_
    :rtype: list[Card] | None
    """
    card_list = list()
    amount = order_amount
    for card in card_rows:
        logger.info(f"\n{card[0].amount=} {amount=}")
        if amount - card[0].amount > 0:
            amount -= card[0].amount
            card_list.append(card[0])
        elif amount - card[0].amount == 0:
            amount -= card[0].amount
            card_list.append(card[0])
            return card_list
        else:
            continue
    text = f"_create_certificates_chain amount not covered {amount=} You must buy codes!!!"
    logger.critical(text)
    await send_telegram_message(text)
    return None


async def _write_verification_result(digi_answer: ResponseDigiseller, db) -> list[str] | None:
    """Write to DB info about transaction

    :param digi_answer: answer from Digiseller
    :type digi_answer: ResponseDigiseller
    :param db: db connection
    :type db: _type_
    :raises Exception: _description_
    :raises Exception: _description_
    :return: _description_
    :rtype: str
    """
    async with db as session:
        async with session.begin():
            code_dal = CodeDAL(session)

            card_rows = await code_dal.get_valide_code()
            if card_rows is None:
                return [
                    "Trouble with get valide code. There was a problem. The support service is already dealing with your issue. You can contact support by ..."
                ]
            give_away_list_cards = await _create_certificates_chain(digi_answer.amount, card_rows)
            logger.debug(f"{give_away_list_cards=}")
            if give_away_list_cards is None:
                return [
                    "No codes to give. There was a problem. The support service is already dealing with your issue. You can contact support by ..."
                ]

            logger.debug(f"{digi_answer.inv=}")
            updated_true = await code_dal.update_card_row(give_away_list_cards, digi_answer.inv, digi_answer.email)
            logger.debug(f"{updated_true=}")
            if not updated_true:
                return [
                    "Some trouble with update card info. There was a problem. The support service is already dealing with your issue. You can contact support by ..."
                ]
            result = [card.card_code for card in give_away_list_cards]
            return result


@user_router.get("/check-code")
async def check_code(request: Request, uniquecode: str, db: AsyncSession = Depends(get_db)):
    if len(uniquecode) != 16:
        raise HTTPException(status_code=422, detail="code incorrcet")

    await _create_new_code(uniquecode, db)

    digi_answer = await _get_verification_result(uniquecode)
    if not await _is_received(digi_answer, db):
        answer = await _write_verification_result(digi_answer, db)
    else:
        answer = ["code has already been issued"]
    return templates.TemplateResponse(
        "codes/index.html", {"request": request, "app_name": APP_NAME, "code_list": answer}
    )
