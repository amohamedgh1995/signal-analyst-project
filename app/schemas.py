from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    telegram_id: int
    username: str

class UserCreate(UserBase):
    full_name: str
    invited_by: Optional[int] = None

class UserOut(UserBase):
    id: int
    full_name: str
    status: str
    join_date: datetime
    subscription_expiry: Optional[datetime] = None
    is_active: bool
    invited_by: Optional[int] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class SwaggerAuthForm(BaseModel):
    username: str
    password: str

# سایر اسکیماها بدون تغییر باقی می‌مانند
# ...

class UserBase(BaseModel):
    telegram_id: int
    username: str
    full_name: str

class UserCreate(UserBase):
    invited_by: Optional[int] = None

class UserOut(UserBase):
    id: int
    status: str
    join_date: datetime
    subscription_expiry: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    amount: int
    currency: str = "USDT"
    payment_method: str

class PaymentCreate(PaymentBase):
    payment_proof: str

class PaymentOut(PaymentBase):
    id: int
    user_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    telegram_id: Optional[int] = None

class SignalBase(BaseModel):
    symbol: str
    direction: str
    entry_price: float
    targets: List[float]
    stop_loss: float
    signal_type: str  # free/vip

class SignalCreate(SignalBase):
    pass

class SignalOut(SignalBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class InvitationBase(BaseModel):
    invitee_username: str
    discount_percent: int = 10

class InvitationCreate(InvitationBase):
    pass

class InvitationOut(InvitationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SupportTicketBase(BaseModel):
    message: str

class SupportTicketCreate(SupportTicketBase):
    pass

class SupportTicketOut(SupportTicketBase):
    id: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentInfo(BaseModel):
    card_number: str
    tron_wallet: str
    vip_price_usd: float
    vip_price_irr: float

# مدل جدید برای احراز هویت Swagger
class SwaggerAuthForm(BaseModel):
    username: str
    password: str