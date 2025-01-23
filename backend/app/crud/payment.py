from sqlmodel import select, Session
from app.models.payment import Payment
from typing import Union, List

def get_payment_by_id(session: Session, payment_id: int) -> Union[Payment, None]:
    statement = select(Payment).where(Payment.paymentId == payment_id)
    return session.exec(statement).first()

def get_all_payments(session: Session) -> List[Payment]:
    statement = select(Payment)
    return list(session.exec(statement).all())

def create_payment(session: Session, payment_data: Payment) -> Payment:
    session.add(payment_data)
    session.commit()
    session.refresh(payment_data)
    return payment_data

def update_payment(session: Session, payment: Payment) -> Payment:
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment

def delete_payment(session: Session, payment: Payment) -> None:
    session.delete(payment)
    session.commit()