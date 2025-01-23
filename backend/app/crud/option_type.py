from sqlmodel import select, Session
from app.models.option_type import OptionType
from typing import Union, List

def get_option_type_by_id(session: Session, option_type_id: int) -> Union[OptionType, None]:
    statement = select(OptionType).where(OptionType.optionTypeId == option_type_id)
    return session.exec(statement).first()

def get_all_option_types(session: Session) -> List[OptionType]:
    statement = select(OptionType)
    return list(session.exec(statement).all())

def create_option_type(session: Session, option_type_data: OptionType) -> OptionType:
    session.add(option_type_data)
    session.commit()
    session.refresh(option_type_data)
    return option_type_data

def update_option_type(session: Session, option_type: OptionType) -> OptionType:
    session.add(option_type)
    session.commit()
    session.refresh(option_type)
    return option_type

def delete_option_type(session: Session, option_type: OptionType) -> None:
    session.delete(option_type)
    session.commit()