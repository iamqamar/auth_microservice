from pydantic import BaseModel, EmailStr


class LoginIn(BaseModel):
    email: EmailStr
    raw_password: str

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshIn(BaseModel):
    refresh_token: str
