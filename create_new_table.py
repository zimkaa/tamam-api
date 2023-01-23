# Work to create new table

import os

from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

REAL_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(REAL_DATABASE_URL, future=True, echo=True, execution_options={"isolation_level": "AUTOCOMMIT"})

df = pd.read_csv("./inser_data_to_db/test_import.csv")

try:
    # df.to_sql("details", engine, replace=True, index=False)
    # df.to_sql('details', con=engine, index=False, index_label='id', if_exists='append')
    df.to_sql("details", con=engine, index=False, if_exists="append")
except Exception:
    print("Sorry, some error has occurred!")
finally:
    engine.dispose()
