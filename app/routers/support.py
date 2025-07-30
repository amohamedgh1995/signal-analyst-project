from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
from ..dependencies import get_current_user

router = APIRouter(prefix="/support", tags=["Support"])

@router.post("/tickets", response_model=schemas.SupportTicketOut)
def create_support_ticket(
    ticket: schemas.SupportTicketCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_ticket = models.SupportTicket(
        user_id=current_user.id,
        message=ticket.message
    )
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket