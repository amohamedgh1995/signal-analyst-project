from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

# تنظیمات پرداخت
PAYMENT_CARD = "6037-9971-1234-5678"  # شماره کارت برای پرداخت‌های ریالی
TRON_WALLET = "TXYZ...abc"  # آدرس ولت TRON
VIP_PRICE_USD = 50  # قیمت اشتراک VIP به دلار
VIP_PRICE_IRR = 5000000  # قیمت اشتراک VIP به تومان

@router.post("/", response_model=schemas.PaymentOut)
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # ایجاد رکورد پرداخت
    new_payment = models.Payment(
        user_id=current_user.id,
        amount=payment.amount,
        currency=payment.currency,
        payment_method=payment.payment_method,
        payment_proof=payment.payment_proof
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

@router.get("/info", response_model=schemas.PaymentInfo)
def get_payment_info():
    return {
        "card_number": PAYMENT_CARD,
        "tron_wallet": TRON_WALLET,
        "vip_price_usd": VIP_PRICE_USD,
        "vip_price_irr": VIP_PRICE_IRR
    }