from sqlmodel import select, Session
from app.models.module_usage_history import ModuleUsageHistory
from typing import Union, List

def get_module_usage_history_by_id(session: Session, usage_id: int) -> Union[ModuleUsageHistory, None]:
    statement = select(ModuleUsageHistory).where(ModuleUsageHistory.moduleUsageId == usage_id)
    return session.exec(statement).first()

def get_all_module_usage_histories(session: Session) -> List[ModuleUsageHistory]:
    statement = select(ModuleUsageHistory)
    return list(session.exec(statement).all())

def create_module_usage_history(session: Session, usage_data: ModuleUsageHistory) -> ModuleUsageHistory:
    session.add(usage_data)
    session.commit()
    session.refresh(usage_data)
    return usage_data

def update_module_usage_history(session: Session, usage: ModuleUsageHistory) -> ModuleUsageHistory:
    session.add(usage)
    session.commit()
    session.refresh(usage)
    return usage

def delete_module_usage_history(session: Session, usage: ModuleUsageHistory) -> None:
    session.delete(usage)
    session.commit()