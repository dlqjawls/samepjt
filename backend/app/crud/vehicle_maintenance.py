from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.vehicle_maintenance import VehicleMaintenance
from typing import Optional
from fastapi import HTTPException

def get_vehicle_maintenance_by_id(session: Session, maintenance_id: Optional[int]) -> Optional[VehicleMaintenance]:
    if maintenance_id is None:
        raise HTTPException(status_code=400, detail="Vehicle Maintenance ID cannot be None")

    statement = select(VehicleMaintenance).where(VehicleMaintenance.maintenanceId == maintenance_id)
    result = session.exec(statement).first()
    
    return result 

def create_vehicle_maintenance(session: Session, maintenance_data: VehicleMaintenance) -> VehicleMaintenance:
    try:
        session.add(maintenance_data)
        session.commit()
        session.refresh(maintenance_data)
        return maintenance_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create vehicle maintenance record")

def update_vehicle_maintenance(session: Session, maintenance: VehicleMaintenance) -> VehicleMaintenance:
    existing_maintenance = get_vehicle_maintenance_by_id(session, maintenance.maintenanceId)
    
    if not existing_maintenance:
        raise HTTPException(status_code=404, detail=f"Vehicle Maintenance with ID {maintenance.maintenanceId} does not exist")
    
    session.add(maintenance)
    session.commit()
    session.refresh(maintenance)
    return maintenance

def delete_vehicle_maintenance(session: Session, maintenance_id: int) -> None:
    maintenance = get_vehicle_maintenance_by_id(session, maintenance_id)
    
    if not maintenance:
        raise HTTPException(status_code=404, detail=f"Vehicle Maintenance with ID {maintenance_id} does not exist")
    
    session.delete(maintenance)
    session.commit()
