from sqlmodel import select, Session
from app.models.option_usage_history import OptionUsageHistory
from typing import Union, List

def get_option_usage_history_by_id(session: Session, usage_id: int) -> Union[OptionUsageHistory, None]:
    statement = select(OptionUsageHistory).where(OptionUsageHistory.optionUsageId == usage_id)
    return session.exec(statement).first()

def get_all_option_usage_histories(session: Session) -> List[OptionUsageHistory]:
    statement = select(OptionUsageHistory)
    return list(session.exec(statement).all())

def create_option_usage_history(session: Session, usage_data: OptionUsageHistory) -> OptionUsageHistory:
    session.add(usage_data)
    session.commit()
    session.refresh(usage_data)
    return usage_data

def update_option_usage_history(session: Session, usage: OptionUsageHistory) -> OptionUsageHistory:
    session.add(usage)
    session.commit()
    session.refresh(usage)
    return usage

def delete_option_usage_history(session: Session, usage: OptionUsageHistory) -> None:
    session.delete(usage)
    session.commit()