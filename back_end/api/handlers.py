import datetime
import hashlib
import json
import time

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request

# from starlette.responses import RedirectResponse
# from starlette.status import HTTP_302_FOUND
import httpx
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import Jinja2Templates

from .models import ResponseDigiseller

from back_end.settings import APP_NAME
from back_end.settings import APILOGIN_URL
from back_end.settings import TEST_CHECK_CODE_URL
from back_end.settings import TEST_DIGISELLER_TOKEN
from back_end.settings import DIGISELLER_TOKEN
from back_end.settings import CHECK_CODE_URL
from back_end.settings import DIGISELLER_ID

from back_end.db.dals import CodeDAL
from back_end.db.session import get_db
from back_end.db.models import Card
from back_end.utils.telegramm import send_telegram_message


TEMPLATES = Jinja2Templates(directory="back_end/templates")
user_router = APIRouter()

TOKEN = None

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


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


async def _get_verification_result(code: str) -> dict:
    """Do request to check number of code

    :param code: number of code
    :type code: str
    :return: answer from Digiseller
    :rtype: dict
    """
    try:
        async with httpx.AsyncClient() as client:
            url = CHECK_CODE_URL.format(token=TOKEN, unique_code=code)
            logger.debug(f"{url=}")
            response = await client.get(url)
            logger.critical(f"_get_verification_result {response.text=}")
            digi_answer = json.loads(response.content)
            logger.debug(f"{digi_answer=}")
    except Exception as error:
        text = f"_get_verification_result trouble with query to Digiseller {error=}"
        logger.error(text)
        await send_telegram_message(text)
        digi_answer = {}
    return digi_answer


async def _get_issued_codes(digi_answer: ResponseDigiseller, db) -> list[Card] | None:
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
            issued_codes = await code_dal.check_code_in_db(inv=digi_answer.inv)
    return issued_codes


async def _create_certificates_chain(order_amount: float, card_rows: list[tuple[Card]]) -> list[Card] | None:
    """Create chain of codes to give for client
    if amount not covered send massage to Telegramm

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


class NoCardError(Exception):
    """No code to give"""

    pass


class WriteToDBError(Exception):
    """Trouble with writing in DB"""

    pass


async def _write_verification_result(digi_answer: ResponseDigiseller, db) -> list[Card]:
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

            card_rows = await code_dal.get_valid_code()
            if card_rows is None:
                text = f"AHTUNG!!! We don't have codes to sell. Customer paid for amount={digi_answer.amount}"
                logger.error(text)
                await send_telegram_message(text)
                raise NoCardError

            give_away_list_cards = await _create_certificates_chain(digi_answer.amount, card_rows)
            logger.debug(f"{give_away_list_cards=}")
            if give_away_list_cards is None:
                text = f"AHTUNG!!! We don't have codes to sell. Customer paid for amount={digi_answer.amount}"
                logger.error(text)
                await send_telegram_message(text)
                raise NoCardError

            logger.debug(f"{digi_answer.inv=}")
            updated_true = await code_dal.update_card_row(give_away_list_cards, digi_answer.inv, digi_answer.email)
            logger.debug(f"{updated_true=}")
            if not updated_true:
                message_string = ""
                for card in give_away_list_cards:
                    message_string += (
                        f"card_id={card[0].card_id} card_code={card[0].card_code} amount={card[0].amount}\n"
                    )
                message_string += f"inv={digi_answer.inv} email={digi_answer.email} time={datetime.datetime.utcnow()}"
                text = f"AHTUNG!!! Can't write to db \namount={digi_answer.amount}\nused chain {message_string}"
                logger.error(text)
                await send_telegram_message(text)
                raise WriteToDBError
            return give_away_list_cards


def get_json_query_data():
    timestamp = time.time_ns()
    string = f"{DIGISELLER_TOKEN}{timestamp}"
    sign = hashlib.sha256(string.encode("utf-8")).hexdigest()
    data = {
        "seller_id": DIGISELLER_ID,
        "timestamp": timestamp,
        "sign": sign,
    }
    return json.dumps(data)


async def get_new_token():
    async with httpx.AsyncClient() as client:
        json_data = get_json_query_data()
        logger.debug(f"{APILOGIN_URL=}")
        response = await client.post(APILOGIN_URL, data=json_data, headers=HEADERS)
        response_dct = response.json()
        if response_dct["retval"] != 0:
            text = f"AHTUNG!!! Bad get token \n{response_dct=}"
            logger.error(text)
            await send_telegram_message(text)
        global TOKEN
        TOKEN = response_dct["token"]


@user_router.post("/check-code")
async def check_code(request: Request, uniquecode: str, db: AsyncSession = Depends(get_db)):
    await _create_new_code(uniquecode, db)
    try:
        await get_new_token()
    except Exception as error:
        logger.error("get_new_token()")
        logger.error(f"{error=}")
        return TEMPLATES.TemplateResponse("codes/trouble.html", {"request": request, "app_name": APP_NAME})

    digi_answer_dict = await _get_verification_result(uniquecode)
    if digi_answer_dict["retval"] != 0:
        text = f"AHTUNG!!! Bad check code \n{uniquecode=}"
        logger.error(text)
        await send_telegram_message(text)
        return TEMPLATES.TemplateResponse("codes/bad_check_result.html", {"request": request, "app_name": APP_NAME})
    digi_answer = ResponseDigiseller(**digi_answer_dict)
    issued_codes = await _get_issued_codes(digi_answer, db)
    if not issued_codes:
        try:
            answer = await _write_verification_result(digi_answer, db)
        except (NoCardError, WriteToDBError):
            logger.error("NoCardError, WriteToDBError")
            return TEMPLATES.TemplateResponse("codes/trouble.html", {"request": request, "app_name": APP_NAME})
        except Exception as error:
            text = f"I don't know this trouble {error=}"
            logger.error(text)
            await send_telegram_message(text)
            return "I don't know this trouble"
    else:
        answer = []
        for card_row in issued_codes:
            answer.append(card_row[0])
    return TEMPLATES.TemplateResponse(
        "codes/index.html", {"request": request, "app_name": APP_NAME, "code_list": answer}
    )
