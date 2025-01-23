from sqlmodel import select, Session
from app.models.option import Option
from typing import Union, List

def get_option_by_id(session: Session, option_id: int) -> Union[Option, None]:
    statement = select(Option).where(Option.optionId == option_id)
    return session.exec(statement).first()

def get_all_options(session: Session) -> List[Option]:
    statement = select(Option)
    return list(session.exec(statement).all())

def create_option(session: Session, option_data: Option) -> Option:
    session.add(option_data)
    session.commit()
    session.refresh(option_data)
    return option_data

def update_option(session: Session, option: Option) -> Option:
    session.add(option)
    session.commit()
    session.refresh(option)
    return option

def delete_option(session: Session, option: Option) -> None:
    session.delete(option)
    session.commit()