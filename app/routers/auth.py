from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel

from app import schemas, models
from app.database import get_db
from app.dependencies import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

# تعریف روتر
router = APIRouter(tags=["Authentication"], prefix="/auth")

# مدل برای لاگین تلگرام
class TelegramLogin(BaseModel):
    telegram_id: int
    username: str
    first_name: str
    last_name: str = None

@router.post("/telegram-login", response_model=schemas.Token)
async def telegram_login(
    user_data: TelegramLogin,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.telegram_id == user_data.telegram_id
    ).first()
    
    if not user:
        user = models.User(
            telegram_id=user_data.telegram_id,
            username=user_data.username,
            full_name=f"{user_data.first_name} {user_data.last_name or ''}",
            status="free",
            is_active=True
        )
        db.add(user)
        db.commit()
    
    access_token = create_access_token(
        data={"sub": str(user.telegram_id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: schemas.UserBase, 
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.telegram_id == form_data.telegram_id
    ).first()
    
    if not user or user.username != form_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram ID یا نام کاربری اشتباه",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری غیرفعال شده است"
        )
    
    access_token = create_access_token(
        data={"sub": str(user.telegram_id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/swagger-token", response_model=schemas.Token, include_in_schema=False)
async def login_for_swagger_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        telegram_id = int(form_data.username)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram ID باید عدد باشد",
        )
    
    user = db.query(models.User).filter(
        models.User.telegram_id == telegram_id,
        models.User.username == form_data.password
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram ID یا نام کاربری اشتباه",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری غیرفعال شده است"
        )
    
    access_token = create_access_token(
        data={"sub": str(user.telegram_id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.UserOut)
def register_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        (models.User.telegram_id == user.telegram_id) | 
        (models.User.username == user.username)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram ID یا نام کاربری قبلاً ثبت شده"
        )
    
    new_user = models.User(
        telegram_id=user.telegram_id,
        username=user.username,
        full_name=user.full_name,
        invited_by=user.invited_by,
        status="free",
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/test-auth", response_model=schemas.UserOut)
def test_authentication(
    current_user: models.User = Depends(get_current_user)
):
    return current_user
