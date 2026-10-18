from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserIn(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    raw_password: str = Field(min_length=8, max_length=50)

    @field_validator("name", mode="before")
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty or whitespace")
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabetic characters and spaces")
        return value.strip()

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Email cannot be empty or whitespace")
        return value.strip().lower()

    @field_validator("raw_password", mode="before")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Password cannot be empty or whitespace")
        if " " in value:
            raise ValueError("Password cannot contain spaces")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char in "@#." for char in value):
            raise ValueError("Password must contain at least one special character (@, #, .)")
        return value

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}

class UserOutAdmin(UserOut):
    is_active: bool

    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None)

    @field_validator("name", mode="before")
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty or whitespace")
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only alphabetic characters and spaces")
        return value.strip()

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Email cannot be empty or whitespace")
        return value.strip().lower()

class PasswordUpdate:
    old_password: str = Field(min_length=8, max_length=50)
    new_password: str = Field(min_length=8, max_length=50)

    @field_validator("old_password", "new_password", mode="before")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Password cannot be empty or whitespace")
        if " " in value:
            raise ValueError("Password cannot contain spaces")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char in "@#." for char in value):
            raise ValueError("Password must contain at least one special character (@, #, .)")
        return value
