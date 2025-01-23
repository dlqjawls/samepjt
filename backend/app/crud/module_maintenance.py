from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.module_maintenance import ModuleMaintenance
from fastapi import HTTPException
from typing import Optional 

def get_module_maintenance_by_id(session: Session, maintenance_id: Optional[int]) -> Optional[ModuleMaintenance]:
  if maintenance_id is None:
    raise HTTPException(status_code=400, detail="Module Maintenance ID cannot be None")
  statement = select(ModuleMaintenance).where(ModuleMaintenance.maintenanceId == maintenance_id)
  result = session.exec(statement).first()

  return result
    

def create_module_maintenance(session: Session, maintenance_data: ModuleMaintenance) -> ModuleMaintenance:
    try:
        session.add(maintenance_data)
        session.commit()
        session.refresh(maintenance_data)
        return maintenance_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create module maintenance record")

def update_module_maintenance(session: Session, maintenance: ModuleMaintenance) -> ModuleMaintenance:
    existing_maintenance = get_module_maintenance_by_id(session, maintenance.maintenanceId)
    
    if not existing_maintenance:
        raise HTTPException(status_code=404, detail=f"Module Maintenance with ID {maintenance.maintenanceId} does not exist")
    
    session.add(maintenance)
    session.commit()
    session.refresh(maintenance)
    return maintenance

def delete_module_maintenance(session: Session, maintenance_id: int) -> None:
    maintenance = get_module_maintenance_by_id(session, maintenance_id)
    
    if not maintenance:
        raise HTTPException(status_code=404, detail=f"Module Maintenance with ID {maintenance_id} does not exist")
    
    session.delete(maintenance)
    session.commit()
