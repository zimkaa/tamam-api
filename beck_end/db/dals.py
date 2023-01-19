from typing import Union
from uuid import UUID

from sqlalchemy import update, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from beck_end.db.models import Code, Card

###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################


class CodeDAL:
    """Data Access Layer for operating code info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_code(self, code: str) -> Code:
        new_code = Code(code=code)
        self.db_session.add(new_code)
        result = await self.db_session.flush()
        logger.debug(f"{result=}")
        return new_code

    async def check_code_in_db(self, inv) -> bool:
        query = select(Card).where(Card.inv == inv)
        res = await self.db_session.execute(query)
        code_row = res.fetchone()
        if code_row is not None:
            logger.critical(f"check_code_in_db code exist in DB {code_row=}")
            return True
        return False

    async def get_valide_code(self):
        query = select(Card).where(Card.is_received == False)
        res = await self.db_session.execute(query)
        code_row = res.fetchall()
        if code_row is not None:
            logger.debug(f"{code_row=}")
            return code_row

    # async def delete_code(self, user_id: UUID) -> Union[UUID, None]:
    #     query = (
    #         update(Code)
    #         .where(and_(Code.code_id == user_id, Code.is_received == True))
    #         .values(is_received=False)
    #         .returning(Code.code_id)
    #     )
    #     res = await self.db_session.execute(query)
    #     deleted_code_id_row = res.fetchone()
    #     if deleted_code_id_row is not None:
    #         return deleted_code_id_row[0]

    # async def get_code_by_id(self, code_id: UUID) -> Union[Code, None]:
    #     query = select(Code).where(Code.code_id == code_id)
    #     res = await self.db_session.execute(query)
    #     code_row = res.fetchone()
    #     if code_row is not None:
    #         return code_row[0]

    async def update_code(self, code_id: UUID, **kwargs) -> Union[UUID, None]:
        query = (
            update(Code)
            .where(and_(Code.code_id == code_id, Code.is_received == True))
            .values(kwargs)
            .returning(Code.code_id)
        )
        res = await self.db_session.execute(query)
        update_code_id_row = res.fetchone()
        if update_code_id_row is not None:
            return update_code_id_row[0]
