from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.module_set import ModuleSet
from typing import Optional, List
from fastapi import HTTPException

def get_module_set_by_id(session: Session, module_set_id: Optional[int]) -> Optional[ModuleSet]:
    if module_set_id is None:
        raise HTTPException(status_code=400, detail="Module Set ID cannot be None")

    statement = select(ModuleSet).where(ModuleSet.moduleSetId == module_set_id)
    result = session.exec(statement).first()

    return result 


def get_all_module_sets(session: Session) -> List[ModuleSet]:
    return list(session.exec(select(ModuleSet)).all())

def create_module_set(session: Session, module_set_data: ModuleSet) -> ModuleSet:
    try:
        session.add(module_set_data)
        session.commit()
        session.refresh(module_set_data)
        return module_set_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create module set")

def update_module_set(session: Session, module_set: ModuleSet) -> ModuleSet:
    existing_module_set = get_module_set_by_id(session, module_set.moduleSetId)
    
    if not existing_module_set:
        raise HTTPException(status_code=404, detail=f"Module Set with ID {module_set.moduleSetId} does not exist")
    
    session.add(module_set)
    session.commit()
    session.refresh(module_set)
    return module_set

def delete_module_set(session: Session, module_set_id: int) -> None:
    module_set = get_module_set_by_id(session, module_set_id)
    
    if not module_set:
        raise HTTPException(status_code=404, detail=f"Module Set with ID {module_set_id} does not exist")
    
    session.delete(module_set)
    session.commit()
