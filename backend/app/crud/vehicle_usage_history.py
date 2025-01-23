from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.vehicle_usage_history import VehicleUsageHistory
from typing import Optional, List
from fastapi import HTTPException

def get_vehicle_usage_history_by_id(session: Session, usage_id: Optional[int]) -> Optional[VehicleUsageHistory]:
    if usage_id is None:
        raise HTTPException(status_code=400, detail="Vehicle Usage ID cannot be None")

    statement = select(VehicleUsageHistory).where(VehicleUsageHistory.vehicleUsageId == usage_id)
    result = session.exec(statement).first()
    
    return result

def get_all_vehicle_usage_histories(session: Session) -> List[VehicleUsageHistory]:
    return list(session.exec(select(VehicleUsageHistory)).all())

def create_vehicle_usage_history(session: Session, usage_data: VehicleUsageHistory) -> VehicleUsageHistory:
    try:
        session.add(usage_data)
        session.commit()
        session.refresh(usage_data)
        return usage_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create vehicle usage history")

def update_vehicle_usage_history(session: Session, usage: VehicleUsageHistory) -> VehicleUsageHistory:
    existing_usage = get_vehicle_usage_history_by_id(session, usage.vehicleUsageId)
    
    if not existing_usage:
        raise HTTPException(status_code=404, detail=f"Vehicle Usage History with ID {usage.vehicleUsageId} does not exist")
    
    session.add(usage)
    session.commit()
    session.refresh(usage)
    return usage

def delete_vehicle_usage_history(session: Session, usage_id: int) -> None:
    usage = get_vehicle_usage_history_by_id(session, usage_id)
    
    if not usage:
        raise HTTPException(status_code=404, detail=f"Vehicle Usage History with ID {usage_id} does not exist")
    
    session.delete(usage)
    session.commit()
