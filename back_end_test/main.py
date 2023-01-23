import json

import httpx
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import ValidationError
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_302_FOUND
from loguru import logger

from .config import settings


logger.add("server.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip")

#########################
# BLOCK WITH API ROUTES #
#########################

# create instance of the app
test_app = FastAPI(title="code checker")

test_app.mount("/static", StaticFiles(directory="back_end_test/static"), name="static")
templates = Jinja2Templates(directory="back_end_test/templates")


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


@test_app.get("/")
def home(request: Request):
    todos = [
        {"id": "test", "title": "title", "is_complete": False},
        {"id": "test", "title": "title", "is_complete": False},
        {"id": "test", "title": "title", "is_complete": False},
        {"id": "test", "title": "title", "is_complete": False},
    ]
    return templates.TemplateResponse(
        "start/index.html", {"request": request, "app_name": settings.app_name, "todo_list": todos}
    )


@test_app.get("/just/{todo_id}")
def just(todo_id: str):
    print(f"{todo_id=}")
    url = test_app.url_path_for("home")

    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@test_app.get("/view-codes")
def just(request: Request):
    codes = [
        {"id": "1", "title": "500"},
        {"id": "2", "title": "300"},
        {"id": "3", "title": "600"},
        {"id": "4", "title": "150"},
    ]

    return templates.TemplateResponse(
        "codes/index.html", {"request": request, "app_name": settings.app_name, "code_list": codes}
    )
