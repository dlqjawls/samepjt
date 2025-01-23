from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.option_maintenance import OptionMaintenance
from typing import Optional
from fastapi import HTTPException

def get_option_maintenance_by_id(session: Session, maintenance_id: Optional[int]) -> Optional[OptionMaintenance]:
    if maintenance_id is None:
        raise HTTPException(status_code=400, detail="Option Maintenance ID cannot be None")
    
    statement = select(OptionMaintenance).where(OptionMaintenance.maintenanceId == maintenance_id)
    result = session.exec(statement).first()
    
    return result 

def create_option_maintenance(session: Session, maintenance_data: OptionMaintenance) -> OptionMaintenance:
    try:
        session.add(maintenance_data)
        session.commit()
        session.refresh(maintenance_data)
        return maintenance_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create option maintenance record")

def update_option_maintenance(session: Session, maintenance: OptionMaintenance) -> OptionMaintenance:
    existing_maintenance = get_option_maintenance_by_id(session, maintenance.maintenanceId)
    
    if not existing_maintenance:
        raise HTTPException(status_code=404, detail=f"Option Maintenance with ID {maintenance.maintenanceId} does not exist")
    
    session.add(maintenance)
    session.commit()
    session.refresh(maintenance)
    return maintenance

def delete_option_maintenance(session: Session, maintenance_id: int) -> None:
    maintenance = get_option_maintenance_by_id(session, maintenance_id)
    
    if not maintenance:
        raise HTTPException(status_code=404, detail=f"Option Maintenance with ID {maintenance_id} does not exist")
    
    session.delete(maintenance)
    session.commit()
