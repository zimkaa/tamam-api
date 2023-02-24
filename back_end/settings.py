"""File with settings and configs for the project"""

import os

from dotenv import load_dotenv


load_dotenv()


CHANNEL_ID = os.getenv("CHANNEL_ID")
print(f"{CHANNEL_ID=}")

TG_TOKEN = os.getenv("TG_TOKEN")
print(f"{TG_TOKEN=}")

TG_URL = os.getenv("TG_URL")

APP_NAME = os.getenv("APP_NAME", "Code checker")

DB_USER = os.getenv("DB_USER")
print(f"{DB_USER=}")

DB_PASS = os.getenv("DB_PASS")

DB_HOST = os.getenv("DB_HOST")
print(f"{DB_HOST=}")

DB_NAME = os.getenv("DB_NAME")

DB_PORT = os.getenv("DB_PORT")
print(f"{DB_PORT=}")

# connect string for the real database
REAL_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"{REAL_DATABASE_URL=}")

TEST_DB_USER = os.getenv("TEST_DB_USER", "postgres_test")

TEST_DB_PASS = os.getenv("TEST_DB_PASS", "postgres_test")

TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")

TEST_DB_NAME = os.getenv("TEST_DB_NAME", "postgres_test")

TEST_DB_PORT = os.getenv("TEST_DB_PORT", "5433")

# connect string for the test database
TEST_DATABASE_URL = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

DIGISELLER_TOKEN = os.getenv("DIGISELLER_TOKEN", "DIGISELLER_TOKEN NOT IN GLOBAL VARIABLES")
print(f"{DIGISELLER_TOKEN=}")

DIGISELLER_ID = os.getenv("DIGISELLER_ID")
print(f"{DIGISELLER_ID=}")

APILOGIN_URL = os.getenv("APILOGIN_URL", "https://api.digiseller.ru/api/apilogin")

TEST_DIGISELLER_TOKEN = os.getenv("TEST_DIGISELLER_TOKEN", "TEST_DIGISELLER_TOKEN")

CHECK_CODE_URL = os.getenv(
    "CHECK_CODE_URL", "https://api.digiseller.ru/api/purchases/unique-code/{unique_code}?token={token}"
)

TEST_CHECK_CODE_URL = os.getenv(
    "TEST_CHECK_CODE_URL", "http://localhost:5000/api/purchases/unique-code/{unique_code}?token={token}"
)
