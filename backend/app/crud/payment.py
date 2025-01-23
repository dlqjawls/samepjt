from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.payment import Payment
from typing import Optional, List
from fastapi import HTTPException

def get_payment_by_id(session: Session, payment_id: Optional[int]) -> Optional[Payment]:
    if payment_id is None:
        raise HTTPException(status_code=400, detail="Payment ID cannot be None")

    statement = select(Payment).where(Payment.paymentId == payment_id)
    result = session.exec(statement).first()
    
    return result

def get_all_payments(session: Session) -> List[Payment]:
    return list(session.exec(select(Payment)).all())

def create_payment(session: Session, payment_data: Payment) -> Payment:
    try:
        session.add(payment_data)
        session.commit()
        session.refresh(payment_data)
        return payment_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create payment")

def update_payment(session: Session, payment: Payment) -> Payment:
    existing_payment = get_payment_by_id(session, payment.paymentId)
    
    if not existing_payment:
        raise HTTPException(status_code=404, detail=f"Payment with ID {payment.paymentId} does not exist")
    
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment

def delete_payment(session: Session, payment_id: int) -> None:
    payment = get_payment_by_id(session, payment_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail=f"Payment with ID {payment_id} does not exist")
    
    session.delete(payment)
    session.commit()
