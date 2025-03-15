from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ..core.config import get_settings
from ..core.security import verify_password, get_password_hash, create_access_token
from ..db.session import get_session
from ..models.user import User, UserCreate, UserRead

settings = get_settings()
router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(*, db: Session = Depends(get_session), user_in: UserCreate):
    # Check if user exists
    user = db.exec(select(User).where(User.username == user_in.username)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Check if email exists
    user = db.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(
    db: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # Get user
    user = db.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    } 