import re
import uuid
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, validator, constr, Field

#########################
# BLOCK WITH API MODELS #
#########################

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""

        orm_mode = True


class ShowCode(TunedModel):
    code_id: uuid.UUID
    code: str
    is_received: bool


# class CodeCreate(BaseModel):
#     code: str

#     @validator("code")
#     def validate_name(cls, value):
#         if len(value) != 16:
#             raise HTTPException(status_code=422, detail="code incorrcet")
#         return value

#     # @validator("surname")
#     # def validate_surname(cls, value):
#     #     if not LETTER_MATCH_PATTERN.match(value):
#     #         raise HTTPException(status_code=422, detail="Surname should contains only letters")
#     #     return value


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class UpdateUserRequest(BaseModel):
    name: Optional[constr(min_length=1)]
    surname: Optional[constr(min_length=1)]
    email: Optional[EmailStr]

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(status_code=422, detail="Name should contains only letters")
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(status_code=422, detail="Surname should contains only letters")
        return value


class UniqueCodeState(BaseModel):
    state: int = Field(description="состояние сделки")
    date_check: str = Field(description="дата проверки")
    date_delivery: str = Field(description="дата доставки")
    date_confirmed: str = Field(description="дата подтверждения")
    date_refuted: str = Field(description="дата отказа")


class Option(BaseModel):
    id: str = Field(description="параметр, который выбрал или указал покупатель")
    name: str = Field(description="название параметра")
    value: str = Field(description="значение параметра, выбранное или указанное покупателем")


class ResponseDigiseller(BaseModel):
    retval: int = Field(description="код выполнения запроса")
    retdesc: str = Field(description="расшифровка кода выполнения запроса")
    inv: int = Field(
        description="уникальный номер оплаченного счёта в системе учета Digiseller настоятельно рекомендуем сохранять это значение в базе и каждый раз проверять его на уникальность, чтобы избежать двойных начислений"
    )
    id_goods: int = Field(description="идентификатор оплаченного товара")
    amount: float = Field(description="сумма, зачисленная на ваш счет")
    type_curr: str = Field(description="валюта платежа, зачисленного на ваш счет (не способ платежа!)")
    profit: str = Field(description="сумма платежа в USD")
    amount_usd: float = Field(description="сумма, зачисленная на ваш счет (за вычетом комиссий)")
    date_pay: str = Field(description="дата и время совершения платежа")
    email: str = Field(description="email покупателя")
    agent_id: int = Field(description="ID партнера, если продажа была совершена с участием партнера")
    agent_percent: int = Field(description="процент партнерского вознаграждения")
    unit_goods: int = Field(description="единица оплаченного товара")
    cnt_goods: int = Field(description="количество единиц оплаченного товара")
    promo_code: str = Field(description="промо-код, использованный покупателем при оплате")
    bonus_code: str = Field(description="промо-код, выданный покупателю в виде бонуса после оплаты")
    cart_uid: str = Field(description="UID корзины")
    unique_code_state: UniqueCodeState = Field(description="уникальный код (состояние и даты проверки)")
    options: list[Option] = Field(description="список параметров")


test_response_digiseller = ResponseDigiseller(
    **{
        "retval": 0,
        "retdesc": "",
        "inv": 0,
        "id_goods": 0,
        "amount": 0.0,
        "type_curr": "",
        "profit": "",
        "amount_usd": 0.0,
        "date_pay": "",
        "email": "",
        "agent_id": 0,
        "agent_percent": 0,
        "unit_goods": 0,
        "cnt_goods": 0,
        "promo_code": "",
        "bonus_code": "",
        "cart_uid": "",
        "unique_code_state": {
            "state": 0,
            "date_check": "",
            "date_delivery": "",
            "date_confirmed": "",
            "date_refuted": "",
        },
        "options": [{"id": "0", "name": "", "value": ""}, {"id": "0", "name": "", "value": ""}],
    }
)
