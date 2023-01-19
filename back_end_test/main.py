import json

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import ValidationError
from fastapi.responses import JSONResponse
import httpx
from loguru import logger


logger.add("server.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip")

#########################
# BLOCK WITH API ROUTES #
#########################

# create instance of the app
test_app = FastAPI(title="code checker")


@test_app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@test_app.get("/api/purchases/unique-code/{unique_code}")
async def send_answer(unique_code: str, token: str):
    logger.debug(f"{type(token)} {token=}")
    logger.debug(f"{type(unique_code)} {unique_code=}")
    with open("back_end_test/digiseller_check.json", "r", encoding="utf-8") as file:
        info = json.load(file)
    return JSONResponse(info)


@test_app.get("/send_request")
async def send_request():
    async with httpx.AsyncClient() as client:
        url = "http://localhost:8000/user/check-code?uniquecode=1234567890123456"
        response = await client.get(url)
        logger.critical(f"{response.text=}")
    return response.text
