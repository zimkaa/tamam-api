import uvicorn
import json
import os
import random
import string
from typing import Any, Generator, Optional
from pathlib import Path

import httpx
from pydantic import BaseModel, Field
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import ValidationError
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_302_FOUND
from loguru import logger
from faker import Faker

from config.config import settings
from response_model.response_model import empty_response_digiseller, ResponseDigiseller


logger.add("test-server.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip")

#########################
# BLOCK WITH API ROUTES #
#########################

# create instance of the app
test_app = FastAPI(title=settings.app_name)

PROJECT_PATH = Path(__file__).parent.resolve()
fake = Faker()


# @test_app.exception_handler(ValidationError)
# async def validation_exception_handler(request: Request, exc: ValidationError):
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content=jsonable_encoder({"detail": exc.errors()}),
#     )


def random_gener() -> Generator[ResponseDigiseller, Any, None]:
    iter_num = 10
    while iter_num != 0:
        empty_response_digiseller.retval = 0
        empty_response_digiseller.amount = random.randint(0, 9) * 100
        empty_response_digiseller.inv = random.randint(0, 9)
        empty_response_digiseller.email = fake.email()
        yield empty_response_digiseller


response_generator_random = random_gener()


def stable_gener() -> Generator[ResponseDigiseller, Any, None]:

    amount1 = [500, 2100, 600, 1500, 500]
    amount = amount1 * 3
    inv = [456, 887, 890, 234, 543, 123, 223, 334, 224, 445, 443, 776, 779, 969, 556]
    email1 = [fake.email(), fake.email(), fake.email(), fake.email(), fake.email()]
    email2 = [fake.email(), fake.email(), fake.email(), fake.email(), fake.email()]
    email3 = [fake.email(), fake.email(), fake.email(), fake.email(), fake.email()]
    email = email1 + email2 + email3
    index = 0
    while True:
        empty_response_digiseller.retval = 0
        empty_response_digiseller.amount = amount[index]
        empty_response_digiseller.inv = inv[index]
        empty_response_digiseller.email = email[index]
        yield empty_response_digiseller
        index += 1
        if index == 15:
            index = 0


response_generator_stable = stable_gener()


def stable_gener_fail() -> Generator[ResponseDigiseller, Any, None]:

    amount = [20, 210000, 60000, 150000, 50000]
    inv = [4564, 8874, 8904, 2344, 5434]
    email = [fake.email(), fake.email(), fake.email(), fake.email(), fake.email()]
    index = 0
    while True:
        empty_response_digiseller.retval = 0
        empty_response_digiseller.amount = amount[index]
        empty_response_digiseller.inv = inv[index]
        empty_response_digiseller.email = email[index]
        yield empty_response_digiseller
        index += 1
        if index == 5:
            index = 0


response_generator_stable_fail = stable_gener_fail()


def error_gener() -> Generator[ResponseDigiseller, Any, None]:
    amount = 2.2
    inv = 99999
    email = fake.email()
    while True:
        empty_response_digiseller.retval = 1
        empty_response_digiseller.amount = amount
        empty_response_digiseller.inv = inv
        empty_response_digiseller.email = email
        yield empty_response_digiseller


response_generator_error = error_gener()


@test_app.get("/api/purchases/unique-code/{unique_code}")
async def send_answer(unique_code: str, token: str):
    logger.debug(f"{type(token)} {token=}")
    logger.debug(f"{type(unique_code)} {unique_code=} len={len(unique_code)}")
    if len(unique_code) != 16:
        logger.debug(f"len={len(unique_code)}")
        result = next(response_generator_error)
        return JSONResponse(result.dict())
    # result = next(response_generator_random)
    # if not result:
    #     result = next(response_generator_stable)

    result = next(response_generator_stable)

    # result = next(response_generator_stable_fail)

    return JSONResponse(result.dict())


@test_app.get("/send_request")
async def send_request():
    async with httpx.AsyncClient() as client:
        letters = string.ascii_lowercase
        rand_string = "".join(random.choice(letters) for i in range(16))
        # url = f"http://localhost:8000/check-code?uniquecode={rand_string}"
        url = f"http://app:8000/check-code?uniquecode={rand_string}"
        response = await client.get(url)
        logger.critical(f"{response.text=}")
    return response.text


# @test_app.get("/")
# def home(request: Request):
#     todos = [
#         {"id": "test", "title": "title", "is_complete": False},
#         {"id": "test", "title": "title", "is_complete": False},
#         {"id": "test", "title": "title", "is_complete": False},
#         {"id": "test", "title": "title", "is_complete": False},
#     ]
#     return templates.TemplateResponse(
#         "start/index.html", {"request": request, "app_name": settings.app_name, "todo_list": todos}
#     )


# @test_app.get("/just/{todo_id}")
# def just(todo_id: str):
#     print(f"{todo_id=}")
#     url = test_app.url_path_for("home")

#     return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


# @test_app.get("/view-codes")
# def just(request: Request):
#     codes = [
#         {"id": "1", "title": "500"},
#         {"id": "2", "title": "300"},
#         {"id": "3", "title": "600"},
#         {"id": "4", "title": "150"},
#     ]

#     return templates.TemplateResponse(
#         "codes/index.html", {"request": request, "app_name": settings.app_name, "code_list": codes}
#     )


if __name__ == "__main__":
    uvicorn.run(test_app, host="0.0.0.0", port=5000)
