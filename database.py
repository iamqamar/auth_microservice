import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

engine = create_engine(
    url=os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False}
)

def get_session():
    with engine.connect() as connection:
        yield connection


class Base(DeclarativeBase):
    pass
