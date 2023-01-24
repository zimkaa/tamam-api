from typing import Union
from uuid import UUID
import json

from pydantic.tools import parse_obj_as
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import asyncio
from loguru import logger

from .models import ResponseDigiseller, test_response_digiseller

# from .models import CodeCreate, ShowUser, DeleteUserResponse, UpdateUserRequest, UpdatedUserResponse
from back_end.settings import CHEK_CODE_URL, TEST_CHEK_CODE_URL, TEST_DIGISELLER_TOKEN, DIGISELLER_TOKEN
from back_end.db.dals import CodeDAL
from back_end.db.session import get_db
from back_end.db.models import Card
from back_end.utils.telegramm import send_telegram_message


user_router = APIRouter()


# async def _create_new_user(body: UserCreate, db) -> ShowUser:
#     async with db as session:
#         async with session.begin():
#             user_dal = UserDAL(session)
#             user = await user_dal.create_user(
#                 name=body.name,
#                 surname=body.surname,
#                 email=body.email,
#             )
#             return ShowUser(
#                 user_id=user.user_id,
#                 name=user.name,
#                 surname=user.surname,
#                 email=user.email,
#                 is_active=user.is_active,
#             )


# async def _delete_user(user_id, db) -> Union[UUID, None]:
#     async with db as session:
#         async with session.begin():
#             user_dal = UserDAL(session)
#             deleted_user_id = await user_dal.delete_user(
#                 user_id=user_id,
#             )
#             return deleted_user_id


# async def _update_user(updated_user_params: dict, user_id: UUID, db) -> Union[UUID, None]:
#     async with db as session:
#         async with session.begin():
#             user_dal = UserDAL(session)
#             updated_user_id = await user_dal.update_user(user_id=user_id, **updated_user_params)
#             return updated_user_id


# async def _get_user_by_id(user_id, db) -> Union[ShowUser, None]:
#     async with db as session:
#         async with session.begin():
#             user_dal = UserDAL(session)
#             user = await user_dal.get_user_by_id(
#                 user_id=user_id,
#             )
#             if user is not None:
#                 return ShowUser(
#                     user_id=user.user_id,
#                     name=user.name,
#                     surname=user.surname,
#                     email=user.email,
#                     is_active=user.is_active,
#                 )


# @user_router.post("/", response_model=ShowUser)
# async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
#     return await _create_new_user(body, db)


# @user_router.delete("/", response_model=DeleteUserResponse)
# async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> DeleteUserResponse:
#     deleted_user_id = await _delete_user(user_id, db)
#     if deleted_user_id is None:
#         raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
#     return DeleteUserResponse(deleted_user_id=deleted_user_id)


# @user_router.get("/", response_model=ShowUser)
# async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)) -> ShowUser:
#     user = await _get_user_by_id(user_id, db)
#     if user is None:
#         raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
#     return user


# @user_router.patch("/", response_model=UpdatedUserResponse)
# async def update_user_by_id(
#     user_id: UUID, body: UpdateUserRequest, db: AsyncSession = Depends(get_db)
# ) -> UpdatedUserResponse:
#     updated_user_params = body.dict(exclude_none=True)
#     if updated_user_params == {}:
#         raise HTTPException(status_code=422, detail="At least one parameter for user update info should be provided")
#     user = await _get_user_by_id(user_id, db)
#     if user is None:
#         raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
#     updated_user_id = await _update_user(updated_user_params=updated_user_params, db=db, user_id=user_id)
#     return UpdatedUserResponse(updated_user_id=updated_user_id)

######################
#      MY CODE       #
######################


async def _create_new_code(code: str, db) -> bool:
    async with db as session:
        async with session.begin():
            code_dal = CodeDAL(session)
            try:
                await code_dal.create_code(code=code)
                return True
            except Exception as error:
                text = f"_create_new_code Base {error=}"
                logger.error(text)
                await send_telegram_message(text)
                return False


async def _get_verification_result(code: str) -> ResponseDigiseller:
    async with httpx.AsyncClient() as client:
        # url = CHEK_CODE_URL.format(token=DIGISELLER_TOKEN, unique_code=code)
        url = TEST_CHEK_CODE_URL.format(token=TEST_DIGISELLER_TOKEN, unique_code=code)
        response = await client.get(url)
        logger.critical(f"_check_code {response.text=}")
        digi_answer = json.loads(response.content)
        # resp = parse_obj_as(ResponseDigiseller, user_dict)
        # digi_answer = ResponseDigiseller(response.content)
    return ResponseDigiseller(**digi_answer)
    # return test_response_digiseller


async def _check_is_received(digi_answer: ResponseDigiseller, db) -> bool:
    async with db as session:
        async with session.begin():
            code_dal = CodeDAL(session)
            exist = await code_dal.check_code_in_db(inv=digi_answer.inv)
            if exist:
                text = f"_check_is_received code has already been issued {exist=}"
                logger.error(text)
                await send_telegram_message(text)
                return True
    return False


async def create_certificates_chain(order_amount: int, store: list[tuple[Card]]) -> list[Card] | None:
    card_list = list()
    amount = order_amount
    for elem in store:
        logger.info(f"\n{elem[0].amount=} {amount=}")
        if amount - elem[0].amount > 0:
            amount -= elem[0].amount
            card_list.append(elem[0])
        elif amount - elem[0].amount == 0:
            amount -= elem[0].amount
            card_list.append(elem[0])
            return card_list
        else:
            continue
    text = f"create_certificates_chain amount not covered {amount=}"
    logger.error(text)
    await send_telegram_message(text)
    return None


async def _write_verification_result(digi_answer: ResponseDigiseller, db) -> str:
    async with db as session:
        async with session.begin():
            code_dal = CodeDAL(session)
            try:
                card_row = await code_dal.get_valide_code()
                give_away_list_cards = await create_certificates_chain(digi_answer.amount, card_row)
                logger.debug(f"{give_away_list_cards=}")
                if not give_away_list_cards:
                    return "There was a problem. The support service is already dealing with your issue. You can contact support by ..."

                logger.debug(f"{digi_answer.inv=}")
                result = await code_dal.update_card_row(give_away_list_cards, digi_answer.inv)
                logger.debug(f"{result=}")
                if not result:
                    return "There was a problem. The support service is already dealing with your issue. You can contact support by ..."
                front_string = " ".join([card.card_code for card in give_away_list_cards])
                return front_string
            except Exception as error:
                text = f"_write_verification_result {error=}"
                logger.critical(text)
                await send_telegram_message(text)
                return "There was a problem. The support service is already dealing with your issue. You can contact support by ..."


@user_router.get("/check-code")
async def check_code(uniquecode: str, db: AsyncSession = Depends(get_db)):
    if len(uniquecode) != 16:
        raise HTTPException(status_code=422, detail="code incorrcet")
    result = await _create_new_code(uniquecode, db)
    if result:
        digi_answer = await _get_verification_result(uniquecode)
        if not await _check_is_received(digi_answer, db):  # TODO check when true
            answer = await _write_verification_result(digi_answer, db)
            return answer
        # if user is None:
        #     raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
        return "Сode has already been issued"
    logger.error(f"{result=}")
    return "An error has occurred. HTML will return in the future"


@user_router.get("/valid", response_model=ResponseDigiseller)
async def valid():
    return test_response_digiseller
