from pydantic import BaseModel, Field


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
