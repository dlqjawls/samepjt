from sqlmodel import select, Session
from app.models.vehicle_usage_history import VehicleUsageHistory
from typing import Union, List

def get_vehicle_usage_history_by_id(session: Session, usage_id: int) -> Union[VehicleUsageHistory, None]:
    statement = select(VehicleUsageHistory).where(VehicleUsageHistory.vehicleUsageId == usage_id)
    return session.exec(statement).first()

def get_all_vehicle_usage_histories(session: Session) -> List[VehicleUsageHistory]:
    statement = select(VehicleUsageHistory)
    return list(session.exec(statement).all())

def create_vehicle_usage_history(session: Session, usage_data: VehicleUsageHistory) -> VehicleUsageHistory:
    session.add(usage_data)
    session.commit()
    session.refresh(usage_data)
    return usage_data

def update_vehicle_usage_history(session: Session, usage: VehicleUsageHistory) -> VehicleUsageHistory:
    session.add(usage)
    session.commit()
    session.refresh(usage)
    return usage

def delete_vehicle_usage_history(session: Session, usage: VehicleUsageHistory) -> None:
    session.delete(usage)
    session.commit()