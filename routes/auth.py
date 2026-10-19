from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from core.setting import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    oauth2_scheme,
    token_blocklist,
    verify_password,
)
from database import Session, get_session
from models.user import User
from schemas.auth import RefreshIn, TokenOut
from schemas.user import UserIn, UserOutAdmin

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/login", response_model=TokenOut)
def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    stmt = select(User).where(User.email == credentials.username.lower())
    user = session.execute(stmt).scalar_one_or_none()

    if not user or not verify_password(password=credentials.password, hash_password=user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return TokenOut(
        access_token = create_access_token(user.id),
        refresh_token = create_refresh_token(user.id)
    )

@router.post("/register", response_model=UserOutAdmin)
def register(user: UserIn, session: Session = Depends(get_session)):
    exist = session.execute(select(User).where(User.email == user.email)).scalar_one_or_none()

    if exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exist"
        )

    new_user: User = User(
        **user.model_dump(exclude={"raw_password"}),
        hashed_password=hash_password(user.raw_password)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

@router.post("/refresh", response_model=TokenOut)
def token_refresh(
    data: RefreshIn,
    session: Session = Depends(get_session)
):
    try:
        payload = decode_token(token=data.refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The token is invalid or expired"
        )

    if payload["type"] != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not a refresh Token"
        )

    user = session.get(User, int(payload["sub"]))

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )

    return TokenOut(
        access_token=create_access_token(user.id),
        refresh_token=data.refresh_token
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not a valid token"
        )

    token_blocklist.add(payload["jti"])
