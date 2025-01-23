from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.option_usage_history import OptionUsageHistory
from typing import Optional, List
from fastapi import HTTPException

def get_option_usage_history_by_id(session: Session, usage_id: Optional[int]) -> Optional[OptionUsageHistory]:
    if usage_id is None:
        raise HTTPException(status_code=400, detail="Option Usage ID cannot be None")

    statement = select(OptionUsageHistory).where(OptionUsageHistory.optionUsageId == usage_id)
    result = session.exec(statement).first()
    
    return result  

def get_all_option_usage_histories(session: Session) -> List[OptionUsageHistory]:
    return list(session.exec(select(OptionUsageHistory)).all())

def create_option_usage_history(session: Session, usage_data: OptionUsageHistory) -> OptionUsageHistory:
    try:
        session.add(usage_data)
        session.commit()
        session.refresh(usage_data)
        return usage_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create option usage history")

def update_option_usage_history(session: Session, usage: OptionUsageHistory) -> OptionUsageHistory:
    existing_usage = get_option_usage_history_by_id(session, usage.optionUsageId)
    
    if not existing_usage:
        raise HTTPException(status_code=404, detail=f"Option Usage History with ID {usage.optionUsageId} does not exist")
    
    session.add(usage)
    session.commit()
    session.refresh(usage)
    return usage

def delete_option_usage_history(session: Session, usage_id: int) -> None:
    usage = get_option_usage_history_by_id(session, usage_id)
    
    if not usage:
        raise HTTPException(status_code=404, detail=f"Option Usage History with ID {usage_id} does not exist")
    
    session.delete(usage)
    session.commit()
