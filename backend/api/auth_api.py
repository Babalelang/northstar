from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_current_user, require_admin
from database.database import get_db
from models.user import User, UserRole
from schemas.auth import LoginRequest, LoginResponse, UserCreate, UserOut, UserUpdate
from services.auth_service import create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()

    # deliberately identical error for "no such user" and "wrong password" -
    # confirming which one it was tells an attacker whether a username exists
    invalid_credentials = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    if not user or not verify_password(payload.password, user.password_hash):
        raise invalid_credentials
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account has been deactivated")

    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    token = create_token(user.id)
    return LoginResponse(token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="That username is already taken")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="That email is already registered")

    item = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole(payload.role),
        is_active=True,
        created_by_id=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    item = db.get(User, user_id)
    if not item:
        raise HTTPException(status_code=404, detail="User not found")

    if item.id == current_user.id and payload.role != "admin":
        raise HTTPException(status_code=400, detail="You can't demote yourself out of admin")
    if item.id == current_user.id and not payload.is_active:
        raise HTTPException(status_code=400, detail="You can't deactivate your own account")

    item.first_name = payload.first_name
    item.last_name = payload.last_name
    item.username = payload.username
    item.email = payload.email
    item.role = UserRole(payload.role)
    item.is_active = payload.is_active
    if payload.password:
        item.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You can't delete your own account")
    item = db.get(User, user_id)
    if not item:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(item)
    db.commit()
    return None
