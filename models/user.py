from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class UserRole(PyEnum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__="user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.user)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=func.now())
