import datetime
import uuid

from sqlalchemy import Column, String, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

##############################
# BLOCK WITH DATABASE MODELS #
##############################

Base = declarative_base()


class Code(Base):
    __tablename__ = "code"

    code_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, nullable=False)
    # surname = Column(String, nullable=False)
    # email = Column(String, nullable=False, unique=True)
    # is_received = Column(Boolean(), default=False)


class Card(Base):
    __tablename__ = "card"

    card_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_code = Column(String, nullable=False)
    surname = Column(String)
    email = Column(String)
    inv = Column(Integer)
    is_received = Column(Boolean(), default=False)
    amount = Column(Integer, nullable=False)
    amount_tl = Column(Integer, nullable=False)
    added_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    used_time = Column(DateTime)
    # tg_user_id = Column(String, nullable=False)
    # tg_user_name = Column(String, nullable=False)
    # card_status = Column(Integer)
