from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.dependencies import get_admin_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.put("/users/{user_id}/status", response_model=schemas.UserOut)
def update_user_status(
    user_id: int, 
    new_status: str,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user)
):
    # اعتبارسنجی وضعیت جدید
    valid_statuses = ["free", "vip", "admin"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"وضعیت نامعتبر. وضعیت‌های مجاز: {', '.join(valid_statuses)}"
        )
    
    # یافتن کاربر و تغییر وضعیت
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد"
        )
    
    user.status = new_status
    
    # اگر کاربر به VIP ارتقا یافت، تاریخ انقضا تنظیم کن
    if new_status == "vip":
        user.subscription_expiry = datetime.utcnow() + timedelta(days=30)
    
    db.commit()
    db.refresh(user)
    return user

@router.put("/payments/{payment_id}/approve", response_model=schemas.PaymentOut)
def approve_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user)
):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="پرداخت یافت نشد"
        )
    
    # تغییر وضعیت پرداخت به تایید شده
    payment.status = "approved"
    
    # ارتقاء کاربر به VIP
    user = payment.user
    user.status = "vip"
    user.subscription_expiry = datetime.utcnow() + timedelta(days=30)
    
    db.commit()
    db.refresh(payment)
    return payment