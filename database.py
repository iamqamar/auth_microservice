from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

engine = create_engine(
    url="sqlite:///./userdb.db",
    connect_args={"check_same_thread": False}
)

def get_session():
    with engine.connect() as connection:
        yield connection


class Base(DeclarativeBase):
    pass
