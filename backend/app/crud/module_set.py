from sqlmodel import select, Session
from app.models.module_set import ModuleSet
from typing import Union, List

def get_module_set_by_id(session: Session, module_set_id: int) -> Union[ModuleSet, None]:
    statement = select(ModuleSet).where(ModuleSet.moduleSetId == module_set_id)
    return session.exec(statement).first()

def get_all_module_sets(session: Session) -> List[ModuleSet]:
    statement = select(ModuleSet)
    return list(session.exec(statement).all())

def create_module_set(session: Session, module_set_data: ModuleSet) -> ModuleSet:
    session.add(module_set_data)
    session.commit()
    session.refresh(module_set_data)
    return module_set_data

def update_module_set(session: Session, module_set: ModuleSet) -> ModuleSet:
    session.add(module_set)
    session.commit()
    session.refresh(module_set)
    return module_set

def delete_module_set(session: Session, module_set: ModuleSet) -> None:
    session.delete(module_set)
    session.commit()