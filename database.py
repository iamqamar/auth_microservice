from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

engine = create_engine(
    url="sqlite:///./userdb.db",
    connect_args={"check_same_thread": False}
)

def get_session():
    with Session(engine) as session:
        yield session


class Base(DeclarativeBase):
    pass
