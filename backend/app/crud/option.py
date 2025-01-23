from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.option import Option
from typing import Optional, List
from fastapi import HTTPException

def get_option_by_id(session: Session, option_id: Optional[int]) -> Optional[Option]:
    if option_id is None:
        raise HTTPException(status_code=400, detail="Option ID cannot be None")

    statement = select(Option).where(Option.optionId == option_id)
    result = session.exec(statement).first()
    
    return result 

def get_all_options(session: Session) -> List[Option]:
    return list(session.exec(select(Option)).all())

def create_option(session: Session, option_data: Option) -> Option:
    try:
        session.add(option_data)
        session.commit()
        session.refresh(option_data)
        return option_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create option")

def update_option(session: Session, option: Option) -> Option:
    existing_option = get_option_by_id(session, option.optionId)
    
    if not existing_option:
        raise HTTPException(status_code=404, detail=f"Option with ID {option.optionId} does not exist")
    
    session.add(option)
    session.commit()
    session.refresh(option)
    return option

def delete_option(session: Session, option_id: int) -> None:
    option = get_option_by_id(session, option_id)
    
    if not option:
        raise HTTPException(status_code=404, detail=f"Option with ID {option_id} does not exist")
    
    session.delete(option)
    session.commit()
