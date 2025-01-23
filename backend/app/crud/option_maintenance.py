from sqlmodel import select, Session
from app.models.module import Module
from typing import Union, List

def get_module_by_id(session: Session, module_id: int) -> Union[Module, None]:
    statement = select(Module).where(Module.moduleId == module_id)
    return session.exec(statement).first()

def get_all_modules(session: Session) -> List[Module]:
    statement = select(Module)
    return list(session.exec(statement).all())

def create_module(session: Session, module_data: Module) -> Module:
    session.add(module_data)
    session.commit()
    session.refresh(module_data)
    return module_data

def update_module(session: Session, module: Module) -> Module:
    session.add(module)
    session.commit()
    session.refresh(module)
    return module

def delete_module(session: Session, module: Module) -> None:
    session.delete(module)
    session.commit()