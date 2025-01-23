from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.module_set_option_type import ModuleSetOptionType
from typing import Optional, List
from fastapi import HTTPException

def get_module_set_option_type_by_id(session: Session, option_type_id: Optional[int]) -> Optional[ModuleSetOptionType]:
    if option_type_id is None:
        raise HTTPException(status_code=400, detail="Module Set Option Type ID cannot be None")
    statement = select(ModuleSetOptionType).where(ModuleSetOptionType.optionTypeId == option_type_id)
    return session.exec(statement).first()  


def get_all_module_set_option_types(session: Session) -> List[ModuleSetOptionType]:
    return list(session.exec(select(ModuleSetOptionType)).all())

def create_module_set_option_type(session: Session, option_type_data: ModuleSetOptionType) -> ModuleSetOptionType:
    try:
        session.add(option_type_data)
        session.commit()
        session.refresh(option_type_data)
        return option_type_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create module set option type")

def update_module_set_option_type(session: Session, option_type: ModuleSetOptionType) -> ModuleSetOptionType:
    existing_option_type = get_module_set_option_type_by_id(session, option_type.optionTypeId)
    
    if not existing_option_type:
        raise HTTPException(status_code=404, detail=f"Module Set Option Type with ID {option_type.optionTypeId} does not exist")
    
    session.add(option_type)
    session.commit()
    session.refresh(option_type)
    return option_type

def delete_module_set_option_type(session: Session, option_type_id: int) -> None:
    option_type = get_module_set_option_type_by_id(session, option_type_id)
    
    if not option_type:
        raise HTTPException(status_code=404, detail=f"Module Set Option Type with ID {option_type_id} does not exist")
    
    session.delete(option_type)
    session.commit()
