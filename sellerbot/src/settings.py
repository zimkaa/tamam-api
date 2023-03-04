"""File with settings and configs for the project"""

import os

from loguru import logger
from dotenv import load_dotenv


load_dotenv()


CHANNEL_ID = os.getenv("CHANNEL_ID")
# logger.info(f"{CHANNEL_ID=}")

ADMIN_CHANNEL_ID = os.getenv("ADMIN_CHANNEL_ID")
# logger.info(f"{ADMIN_CHANNEL_ID=}")

TG_TOKEN = os.getenv("TG_TOKEN")
# logger.info(f"{TG_TOKEN=}")

TG_URL = os.getenv("TG_URL")
# logger.info(f"{TG_URL=}")

DB_USER = os.getenv("DB_USER")
# logger.info(f"{DB_USER=}")

DB_PASS = os.getenv("DB_PASS")

DB_HOST = os.getenv("DB_HOST")
# logger.info(f"{DB_HOST=}")

DB_NAME = os.getenv("DB_NAME")

DB_PORT = os.getenv("DB_PORT")
# logger.info(f"{DB_PORT=}")

REAL_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# logger.info(f"{REAL_DATABASE_URL=}")
