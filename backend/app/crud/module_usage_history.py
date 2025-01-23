from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.module_usage_history import ModuleUsageHistory
from typing import Optional, List
from fastapi import HTTPException

def get_module_usage_history_by_id(session: Session, usage_id: Optional[int]) -> Optional[ModuleUsageHistory]:
    if usage_id is None:
        raise HTTPException(status_code=400, detail="Module Usage History ID cannot be None")
    statement = select(ModuleUsageHistory).where(ModuleUsageHistory.moduleUsageId == usage_id)
    result = session.exec(statement).first()
    
    return result  

def get_all_module_usage_histories(session: Session) -> List[ModuleUsageHistory]:
    return list(session.exec(select(ModuleUsageHistory)).all())

def create_module_usage_history(session: Session, usage_data: ModuleUsageHistory) -> ModuleUsageHistory:
    try:
        session.add(usage_data)
        session.commit()
        session.refresh(usage_data)
        return usage_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create module usage history")

def update_module_usage_history(session: Session, usage: ModuleUsageHistory) -> ModuleUsageHistory:
    existing_usage = get_module_usage_history_by_id(session, usage.moduleUsageId)
    
    if not existing_usage:
        raise HTTPException(status_code=404, detail=f"Module Usage History with ID {usage.moduleUsageId} does not exist")
    
    session.add(usage)
    session.commit()
    session.refresh(usage)
    return usage

def delete_module_usage_history(session: Session, usage_id: int) -> None:
    usage = get_module_usage_history_by_id(session, usage_id)
    
    if not usage:
        raise HTTPException(status_code=404, detail=f"Module Usage History with ID {usage_id} does not exist")
    
    session.delete(usage)
    session.commit()
