from sqlmodel import select, Session
from app.models.module_set_option_type import ModuleSetOptionType
from typing import Union, List, Sequence

def get_module_set_option_type_by_id(session: Session, option_type_id: int) -> Union[ModuleSetOptionType, None]:
    statement = select(ModuleSetOptionType).where(ModuleSetOptionType.optionTypeId == option_type_id)
    return session.exec(statement).first()

def get_all_module_set_option_types(session: Session) -> Sequence[ModuleSetOptionType]:
    statement = select(ModuleSetOptionType)
    return session.exec(statement).all()

def create_module_set_option_type(session: Session, option_type_data: ModuleSetOptionType) -> ModuleSetOptionType:
    session.add(option_type_data)
    session.commit()
    session.refresh(option_type_data)
    return option_type_data

def update_module_set_option_type(session: Session, option_type: ModuleSetOptionType) -> ModuleSetOptionType:
    session.add(option_type)
    session.commit()
    session.refresh(option_type)
    return option_type

def delete_module_set_option_type(session: Session, option_type: ModuleSetOptionType) -> None:
    session.delete(option_type)
    session.commit()