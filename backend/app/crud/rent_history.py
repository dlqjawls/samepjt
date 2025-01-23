from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.rent_history import RentHistory
from typing import Optional, List
from fastapi import HTTPException

def get_rent_history_by_id(session: Session, rent_id: Optional[int]) -> Optional[RentHistory]:
    if rent_id is None:
        raise HTTPException(status_code=400, detail="Rent ID cannot be None")

    statement = select(RentHistory).where(RentHistory.rentId == rent_id)
    result = session.exec(statement).first()
    
    return result  

def get_all_rent_histories(session: Session) -> List[RentHistory]:
    return list(session.exec(select(RentHistory)).all())

def create_rent_history(session: Session, rent_history_data: RentHistory) -> RentHistory:
    try:
        session.add(rent_history_data)
        session.commit()
        session.refresh(rent_history_data)
        return rent_history_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create rent history")

def update_rent_history(session: Session, rent_history: RentHistory) -> RentHistory:
    existing_rent_history = get_rent_history_by_id(session, rent_history.rentId)
    
    if not existing_rent_history:
        raise HTTPException(status_code=404, detail=f"Rent History with ID {rent_history.rentId} does not exist")
    
    session.add(rent_history)
    session.commit()
    session.refresh(rent_history)
    return rent_history

def delete_rent_history(session: Session, rent_id: int) -> None:
    rent_history = get_rent_history_by_id(session, rent_id)
    
    if not rent_history:
        raise HTTPException(status_code=404, detail=f"Rent History with ID {rent_id} does not exist")
    
    session.delete(rent_history)
    session.commit()
