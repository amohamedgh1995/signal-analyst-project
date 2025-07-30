from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, index=True)
    full_name = Column(String)
    status = Column(String, default="free")  # free/vip/admin
    join_date = Column(DateTime, default=datetime.utcnow)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    subscription_expiry = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # روابط
    invited_users = relationship("User", remote_side=[id])
    payments = relationship("Payment", back_populates="user")
    created_signals = relationship("Signal", back_populates="creator")
    support_tickets = relationship("SupportTicket", back_populates="user")
    invitations_sent = relationship("Invitation", foreign_keys="[Invitation.inviter_id]", back_populates="inviter")
    invitations_received = relationship("Invitation", foreign_keys="[Invitation.invitee_id]", back_populates="invitee")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    currency = Column(String, default="USDT")
    payment_method = Column(String)  # card/trx
    payment_proof = Column(String)  # URL to image
    status = Column(String, default="pending")  # pending/approved/rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    user = relationship("User", back_populates="payments")

class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    direction = Column(String)  # buy/sell
    entry_price = Column(Float)
    targets = Column(Text)  # JSON array as string
    stop_loss = Column(Float)
    signal_type = Column(String)  # free/vip
    status = Column(String, default="active")  # active/closed
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # روابط
    creator = relationship("User", back_populates="created_signals")

class Invitation(Base):
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    inviter_id = Column(Integer, ForeignKey("users.id"))
    invitee_id = Column(Integer, ForeignKey("users.id"))
    discount_percent = Column(Integer, default=10)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    inviter = relationship("User", foreign_keys=[inviter_id], back_populates="invitations_sent")
    invitee = relationship("User", foreign_keys=[invitee_id], back_populates="invitations_received")

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    status = Column(String, default="open")  # open/closed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # روابط
    user = relationship("User", back_populates="support_tickets")