from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
from app import schemas, models
from app.database import get_db
from app.dependencies import get_current_user, get_admin_user

router = APIRouter(prefix="/signals", tags=["Signals"])

@router.post("/", response_model=schemas.SignalOut)
def create_signal(
    signal: schemas.SignalCreate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user)
):
    # تبدیل لیست targets به JSON string
    targets_json = json.dumps(signal.targets)
    
    db_signal = models.Signal(
        symbol=signal.symbol,
        direction=signal.direction,
        entry_price=signal.entry_price,
        targets=targets_json,
        stop_loss=signal.stop_loss,
        signal_type=signal.signal_type,
        created_by=admin_user.id
    )
    
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    return db_signal

@router.get("/", response_model=list[schemas.SignalOut])
def get_signals(
    signal_type: str = "free",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # اگر کاربر VIP نیست فقط سیگنال‌های رایگان رو برگردون
    if signal_type == "vip" and current_user.status != "vip":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="برای مشاهده سیگنال‌های VIP نیاز به اشتراک دارید"
        )
    
    signals = db.query(models.Signal).filter(
        models.Signal.signal_type == signal_type,
        models.Signal.status == "active"
    ).all()
    return signals