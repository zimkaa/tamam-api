from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from fastapi.routing import APIRouter
from loguru import logger

from .api.handlers import user_router
from .settings import APP_NAME


logger.add("server.log", format="{time} {level} {message}", level="DEBUG", rotation="10 MB", compression="zip")

#########################
# BLOCK WITH API ROUTES #
#########################

# create instance of the app
app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory="back_end/static", html=True), name="static")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://0.0.0.0",
    "http://0.0.0.0:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create the instance for the routes
main_api_router = APIRouter()

# set routes to the app instance
main_api_router.include_router(user_router, tags=["base"])
app.include_router(main_api_router)
