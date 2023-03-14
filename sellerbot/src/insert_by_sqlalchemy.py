import csv
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from loguru import logger

from src.db.models import Card
from src.settings import DB_USER
from src.settings import DB_PASS
from src.settings import DB_HOST
from src.settings import DB_NAME
from src.settings import DB_PORT


REAL_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

PROJECT_PATH = Path(__file__).parent.resolve()

engine = create_engine(REAL_DATABASE_URL, future=True, execution_options={"isolation_level": "AUTOCOMMIT"})

Session = sessionmaker(engine)


def check_duplicate(session: sessionmaker, card_code) -> None | str:
    query = select(Card).where(Card.card_code == card_code)
    res = session.execute(query)
    code_row = res.fetchone()
    if code_row is None:
        return None
    text = f"\n{card_code}"
    return text


def message_write(message: list[str]) -> None | str:
    text = ""
    duplicates_count = 0
    with Session() as session:
        with session.begin():
            reader = csv.reader(message)
            keys = ["card_code", "amount", "amount_tl"]
            for record in reader:
                data_to_write = dict(zip(keys, record))
                new_card = Card(**data_to_write)
                if new_text := check_duplicate(session, new_card.card_code):
                    text += new_text
                    duplicates_count += 1
                else:
                    session.add(new_card)
            session.flush()

    if text:
        start = "Такой/такие уже был добавлен!\n"
        text_send = start + text + f"\nDuplicates count: {duplicates_count}"
        return text_send
