# Work to create new table

import argparse
import os
import uuid
import csv
import datetime
import requests

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from dotenv import load_dotenv


load_dotenv()

# создаём парсер аргументов и передаём их
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--force", action="store_true", help="write without checking duplicate")
args = vars(ap.parse_args())

FORCE = False
if args["force"]:
    FORCE = True

print(f"{FORCE=}")

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")
CHANNEL_ID = os.getenv("CHANNEL_ID")
TG_TOKEN = os.getenv("TG_TOKEN")
TG_URL = os.getenv("TG_URL")

REAL_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Base = declarative_base()


class Card(Base):
    __tablename__ = "details"

    card_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_code = Column(String, nullable=False)
    surname = Column(String)
    email = Column(String)
    inv = Column(Integer, unique=True)
    is_received = Column(Boolean(), default=False)
    amount = Column(Integer, nullable=False)
    amount_tl = Column(Integer, nullable=False)
    added_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    used_time = Column(DateTime)


engine = create_engine(REAL_DATABASE_URL, future=True, echo=True, execution_options={"isolation_level": "AUTOCOMMIT"})

Base.metadata.create_all(engine)

Session = sessionmaker(engine)


def send_message(text: str) -> None:
    method = TG_URL + TG_TOKEN + "/sendMessage"  # type: ignore
    response = requests.post(
        method,
        data={
            "chat_id": CHANNEL_ID,  # type: ignore
            "text": text,  # type: ignore
        },
    )
    if response.status_code != 200:
        raise Exception("Check codes!!! And we have some trouble with TG")


def check_duplicate(session: sessionmaker, card_code) -> None | str:
    query = select(Card).where(Card.card_code == card_code)
    res = session.execute(query)
    code_row = res.fetchone()
    if code_row is None:
        return None
    text = f"\n{card_code}"
    print(f"\n{card_code=}")
    return text


def main():
    text = ""
    with Session() as session:
        with session.begin():
            with open("./inser_data_to_db/test_import.csv", "r") as file:
                reader = csv.reader(file)
                keys = next(reader)  # This skips the 1st row which is the header.
                for record in reader:
                    data_to_write = dict(zip(keys, record))
                    new_card = Card(**data_to_write)
                    if FORCE:
                        session.add(new_card)
                    else:
                        if new_text := check_duplicate(session, new_card.card_code):
                            text += new_text
                        else:
                            session.add(new_card)
                    # query = select(Card).where(Card.card_code == new_card.card_code)
                    # res = session.execute(query)
                    # code_row = res.fetchone()
                    # if code_row is not None:
                    #     text += f"\n{new_card.card_code}"
                    #     print(f"\n{new_card.card_code=}")
                    # else:
                    #     session.add(new_card)
            session.flush()

        # intersections = session.execute("SELECT card_code FROM details GROUP BY card_code HAVING count(*)>1")
        # quety_intersections = select(Card.card_code).group_by(Card.card_code).having(func.count(Card.card_code) > 1)
        # intersections = session.execute(quety_intersections)
        # # print(f"{intersections.fetchall()=}")

        # intersections_list = list()
        # for element in intersections.fetchall():
        #     intersections_list.append(element[0])
        # if intersections_list:
        #     element_lts = list()
        #     text = "Проверь код! Такой уже был добавлен!\n"
        #     for elem in intersections_list:
        #         # sql5 = f"SELECT card_id, card_code, inv, added_time, used_time FROM details WHERE card_code='{elem}';"
        #         sql5 = select(Card.card_id, Card.card_code, Card.inv, Card.added_time, Card.used_time).where(
        #             Card.card_code == elem
        #         )
        #         intersection = session.execute(sql5).fetchall()
        #         text += f"\n{elem} имеет {len(intersection)} повторений"
        #         element_lts.append(intersection)
        #     text += "\n"
        #     text_table = ""
        #     for rows in element_lts:
        #         text_table += f"\n{rows[0][1]}\n----------\n"
        #         for row in rows:
        #             text_table += f"{row[0]} {row[2]} {row[3]} {row[4]}"
        #         text_table += "\n--------"

        #     text += text_table
        #     channel_id = CHANNEL_ID
        #     url = TG_URL
        #     token = TG_TOKEN
        #     url += token  # type: ignore
        #     method = url + "/sendMessage"
        #     response = requests.post(
        #         method,
        #         data={
        #             "chat_id": channel_id,  # type: ignore
        #             "text": text,  # type: ignore
        #         },
        #     )
        #     if response.status_code != 200:
        #         raise Exception("Check codes!!! And we have some trouble with TG")

    if text:
        start = "Проверь код! Такой уже был добавлен!\n"
        text_send = start + text
        send_message(text_send)


if __name__ == "__main__":
    main()


# # with Session() as session:
# #     with session.begin():
# session = Session()
# session.begin()
# with open("./inser_data_to_db/test_import.csv", "r") as file:
#     reader = csv.reader(file)
#     keys = next(reader)  # This skips the 1st row which is the header.
#     for record in reader:
#         data_to_write = dict(zip(keys, record))
#         new_card = Card(**data_to_write)
#         query = select(Card).where(Card.card_code == new_card.card_code)
#         res = session.execute(query)
#         code_row = res.fetchone()
#         if code_row is not None:
#             print(f"\n\n{new_card.card_code=}")
#             raise Exception(f"Check codes!!! Already exist!!! {new_card.card_code}")
#         else:
#             session.add(new_card)
# session.flush()
# session.close()

# # intersections = session.execute("SELECT card_code FROM details GROUP BY card_code HAVING count(*)>1")
# # quety_intersections = select(Card.card_code).group_by(Card.card_code).having(func.count(Card.card_code) > 1)
# # intersections = session.execute(quety_intersections)
# # print(f"{intersections.fetchall()=}")

# # intersections_list = list()
# # for element in intersections.fetchall():
# #     intersections_list.append(element[0])
# # if intersections_list:
# #     element_lts = list()
# #     text = "Проверь код! Такой уже был добавлен!\n"
# #     for elem in intersections_list:
# #         # sql5 = f"SELECT card_id, card_code, inv, added_time, used_time FROM details WHERE card_code='{elem}';"
# #         sql5 = select(Card.card_id, Card.card_code, Card.inv, Card.added_time, Card.used_time).where(
# #             Card.card_code == elem
# #         )
# #         intersection = session.execute(sql5).fetchall()
# #         text += f"\n{elem} имеет {len(intersection)} повторений"
# #         element_lts.append(intersection)
# #     text += "\n"
# #     text_table = ""
# #     for rows in element_lts:
# #         text_table += f"\n{rows[0][1]}\n----------\n"
# #         for row in rows:
# #             text_table += f"{row[0]} {row[2]} {row[3]} {row[4]}"
# #         text_table += "\n--------"

# #     text += text_table
# #     channel_id = CHANNEL_ID
# #     url = TG_URL
# #     token = TG_TOKEN
# #     url += token  # type: ignore
# #     method = url + "/sendMessage"
# #     response = requests.post(
# #         method,
# #         data={
# #             "chat_id": channel_id,  # type: ignore
# #             "text": text,  # type: ignore
# #         },
# #     )
# #     if response.status_code != 200:
# #         raise Exception("Check codes!!! And we have some trouble with TG")
