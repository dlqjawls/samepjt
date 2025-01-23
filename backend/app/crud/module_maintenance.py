from sqlmodel import select, Session
from app.models.module_maintenance import ModuleMaintenance
from typing import Union

def get_module_maintenance_by_id(session: Session, maintenance_id: int) -> Union[ModuleMaintenance, None]:
    statement = select(ModuleMaintenance).where(ModuleMaintenance.maintenanceId == maintenance_id)
    return session.exec(statement).first()

def create_module_maintenance(session: Session, maintenance_data: ModuleMaintenance) -> ModuleMaintenance:
    session.add(maintenance_data)
    session.commit()
    session.refresh(maintenance_data)
    return maintenance_data

def update_module_maintenance(session: Session, maintenance: ModuleMaintenance) -> ModuleMaintenance:
    session.add(maintenance)
    session.commit()
    session.refresh(maintenance)
    return maintenance

def delete_module_maintenance(session: Session, maintenance: ModuleMaintenance) -> None:
    session.delete(maintenance)
    session.commit()