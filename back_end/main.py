from fastapi import FastAPI
from fastapi import Request
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import ValidationError
from starlette.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
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


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


# create the instance for the routes
main_api_router = APIRouter()

# set routes to the app instance
main_api_router.include_router(user_router, tags=["base"])
app.include_router(main_api_router)
