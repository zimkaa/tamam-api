import os

from dotenv import load_dotenv
from pydantic import BaseSettings


load_dotenv()

TEST_APP_NAME = os.getenv("TEST_APP_NAME", "my test api server")


class Settings(BaseSettings):
    app_name = TEST_APP_NAME
    # db_sqlite_url = os.getenv("SQLALCHEMY_DATABASE_URI")
    # db_postgre_url = os.getenv('POSTGRES_DB')

    class Config:
        env_file: str = "../.env"


settings = Settings()
