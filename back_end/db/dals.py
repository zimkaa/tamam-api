import datetime
from uuid import UUID

from sqlalchemy import update, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from back_end.db.models import Code, Card
from back_end.utils.telegram import send_telegram_message

###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################


class CodeDAL:
    """Data Access Layer for operating code info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_code(self, code: str) -> Code:
        logger.info("create_code")
        new_code = Code(code=code)
        self.db_session.add(new_code)
        result = await self.db_session.flush()
        # TODO WTF???? why result=None????
        logger.debug(f"{result=}")
        return new_code

    async def check_code_in_db(self, inv) -> list[Card] | None:
        logger.info("check_code_in_db")
        try:
            query = select(Card).where(Card.inv == inv)
            res = await self.db_session.execute(query)
            code_row = res.fetchall()
            if code_row is not None:
                logger.info(f"check_code_in_db code exist in DB {type(code_row)} {code_row=}")
                return code_row
        except Exception as error:
            text = f"check_code_in_db unexpected error {error=}"
            logger.error(text)
            await send_telegram_message(text)
        return None

    async def get_valid_code(self) -> list[tuple[Card]] | None:
        """Get code that not used yet

        :return: list of Card elements or None
        :rtype: list[tuple[Card]] | None
        """
        logger.info("get_valid_code")
        try:
            query = select(Card).where(Card.is_received == False).order_by(Card.amount.desc())
            res = await self.db_session.execute(query)
            code_rows = res.fetchall()
            if code_rows is not None:
                # logger.debug(f"{code_rows=}")
                return code_rows
        except Exception as error:
            text = f"update_card_row unexpected error {error=}"
            logger.error(text)
            await send_telegram_message(text)
        return None

    async def update_card(self, card_id: UUID, **kwargs) -> UUID | None:
        logger.info("update_card")
        logger.critical(f"{type(kwargs)} {kwargs=}")
        query = (
            update(Card)
            .where(and_(Card.card_id == card_id, Card.is_received == False))
            .values(kwargs)
            .returning(Card.card_id)
        )
        res = await self.db_session.execute(query)
        update_card_id_row = res.fetchone()
        if update_card_id_row is not None:
            return update_card_id_row[0]
        logger.critical(f"update_card trouble!!! {card_id=}")
        return None

    async def update_card_row(self, row_list: list[Card], inv: int, email: str) -> bool:
        """Update row in DB

        :param row_list: rows to update
        :type row_list: list[Card]
        :param inv: unique transaction identifier
        :type inv: int
        :param email: user email
        :type email: str
        :return: done or not
        :rtype: bool
        """
        logger.info("update_card_row")
        try:
            for row in row_list:
                rows_to_change = {
                    "inv": inv,
                    "is_received": True,
                    "used_time": datetime.datetime.utcnow(),
                    "email": email,
                }
                logger.debug(f"{rows_to_change=}")
                executed = await self.update_card(row.card_id, **rows_to_change)
                if not executed:
                    text = f"update_card_row FAIL {row.card_id=}"
                    logger.error(text)
                    await send_telegram_message(text)
                    return False
        except Exception as error:
            text = f"update_card_row unexpected error {error=}"
            logger.error(text)
            await send_telegram_message(text)
            return False
        return True
