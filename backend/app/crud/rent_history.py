from sqlmodel import select, Session
from app.models.rent_history import RentHistory
from typing import Union, List

def get_rent_history_by_id(session: Session, rent_id: int) -> Union[RentHistory, None]:
    statement = select(RentHistory).where(RentHistory.rentId == rent_id)
    return session.exec(statement).first()

def get_all_rent_histories(session: Session) -> List[RentHistory]:
    statement = select(RentHistory)
    return list(session.exec(statement).all())

def create_rent_history(session: Session, rent_history_data: RentHistory) -> RentHistory:
    session.add(rent_history_data)
    session.commit()
    session.refresh(rent_history_data)
    return rent_history_data

def update_rent_history(session: Session, rent_history: RentHistory) -> RentHistory:
    session.add(rent_history)
    session.commit()
    session.refresh(rent_history)
    return rent_history

def delete_rent_history(session: Session, rent_history: RentHistory) -> None:
    session.delete(rent_history)
    session.commit()