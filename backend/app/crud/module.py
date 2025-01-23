from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.module import Module
from typing import Optional, List
from fastapi import HTTPException

def get_module_by_id(session: Session, module_id: Optional[int]) -> Optional[Module]:
    if module_id is None:
        raise HTTPException(status_code=400, detail="Module ID cannot be None")
    
    statement = select(Module).where(Module.moduleId == module_id)
    result = session.exec(statement).first()

    return result


def get_all_modules(session: Session) -> List[Module]:
    return list(session.exec(select(Module)).all())

def create_module(session: Session, module_data: Module) -> Module:
    try:
        session.add(module_data)
        session.commit()
        session.refresh(module_data)
        return module_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create module")

def update_module(session: Session, module: Module) -> Module:
    existing_module = get_module_by_id(session, module.moduleId)
    
    if not existing_module:
        raise HTTPException(status_code=404, detail=f"Module with ID {module.moduleId} does not exist")
    
    session.add(module)
    session.commit()
    session.refresh(module)
    return module

def delete_module(session: Session, module_id: int) -> None:
    module = get_module_by_id(session, module_id)
    
    if not module:
        raise HTTPException(status_code=404, detail=f"Module with ID {module_id} does not exist")
    
    session.delete(module)
    session.commit()
