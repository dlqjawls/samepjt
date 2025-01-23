from sqlmodel import select, Session, func
from sqlalchemy.exc import IntegrityError
from app.models import OptionType, Option, ModuleSetOptionType
from typing import Optional, List, Tuple
from fastapi import HTTPException

def get_option_type_by_id(session: Session, option_type_id: Optional[int]) -> Optional[OptionType]:
    if option_type_id is None:
        raise HTTPException(status_code=400, detail="Option Type ID cannot be None")
    
    statement = select(OptionType).where(OptionType.optionTypeId == option_type_id)
    result = session.exec(statement).first()
    
    return result  

def get_option_types_by_module_set_id(session: Session, module_set_id: int) -> List[Tuple[OptionType, ModuleSetOptionType]]:
    statement = (
        select(OptionType, ModuleSetOptionType)
        .join(ModuleSetOptionType, ModuleSetOptionType.optionTypeId == OptionType.optionTypeId)
        .where(ModuleSetOptionType.moduleSetId == module_set_id)
    )
    result = list(session.exec(statement).all())
    
    return result

def get_all_option_types(session: Session) -> List[OptionType]:
    return list(session.exec(select(OptionType)).all())

def get_option_counts_by_type(session: Session) -> dict:
    statement = select(Option.optionType, func.count(Option.optionType)).group_by(Option.optionType)
    return dict(session.exec(statement).all())

def create_option_type(session: Session, option_type_data: OptionType) -> OptionType:
    try:
        session.add(option_type_data)
        session.commit()
        session.refresh(option_type_data)
        return option_type_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create option type")

def update_option_type(session: Session, option_type: OptionType) -> OptionType:
    existing_option_type = get_option_type_by_id(session, option_type.optionTypeId)
    
    if not existing_option_type:
        raise HTTPException(status_code=404, detail=f"Option Type with ID {option_type.optionTypeId} does not exist")
    
    session.add(option_type)
    session.commit()
    session.refresh(option_type)
    return option_type

def delete_option_type(session: Session, option_type_id: int) -> None:
    option_type = get_option_type_by_id(session, option_type_id)
    
    if not option_type:
        raise HTTPException(status_code=404, detail=f"Option Type with ID {option_type_id} does not exist")
    
    session.delete(option_type)
    session.commit()
