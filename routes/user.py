from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from core.setting import get_current_user, hash_password, require_admin
from database import Session, get_session
from models.user import User, UserRole
from schemas.user import PasswordUpdate, UserOut, UserOutAdmin, UserUpdate

router = APIRouter(prefix="/users")


@router.get("/me", response_model=UserOut, tags=["user"])
def fetch_current_user(
    user : User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return user

@router.patch("/me", response_model=UserOut, tags=["user"])
def update_user(
    user: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    user_data = user.model_dump(exclude_none=True, exclude_unset=True)

    for field, value in user_data.items():
        setattr(current_user, field, value)

    session.commit()
    session.refresh(current_user)

    return current_user

@router.patch("/password", status_code=status.HTTP_202_ACCEPTED, tags=["user"])
def update_password(
    passwd: PasswordUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    current_user.hashed_password = hash_password(passwd.new_password)

    session.commit()

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, tags=["user"])
def deactive_user(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    current_user.is_active = False

    session.commit()


# --- ADMIN SECTION ---
@router.get("/", response_model=list[UserOutAdmin], tags=["admin"])
def fetch_users(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=25),
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    stmt = select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
    users = session.execute(stmt).scalars().all()

    return users

@router.get("/{id}", response_model=UserOutAdmin, tags=["admin"])
def fetch_user(
    id: int,
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    user = session.get(User, id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

@router.patch("/{id}/role", response_model=UserOutAdmin, tags=["admin"])
def change_role(
    id: int,
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    user = session.get(User, id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.role == UserRole.user:
        user.role = UserRole.admin
    elif user.role == UserRole.admin:
        user.role = UserRole.user

    session.commit()
    session.refresh(user)

    return user

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["admin"])
def delete_user(
    id: int,
    session: Session = Depends(get_session),
    _ = Depends(require_admin)
):
    user = session.get(User, id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    session.delete(user)
    session.commit()
