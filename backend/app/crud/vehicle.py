from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from app.models.vehicle import Vehicle
from typing import Optional, List
from fastapi import HTTPException

def get_vehicle_by_id(session: Session, vehicle_id: Optional[int]) -> Optional[Vehicle]:
    if vehicle_id is None:
        raise HTTPException(status_code=400, detail="Vehicle ID cannot be None")

    statement = select(Vehicle).where(Vehicle.vehicleId == vehicle_id)
    result = session.exec(statement).first()
    
    return result 

def get_all_vehicles(session: Session) -> List[Vehicle]:
    return list(session.exec(select(Vehicle)).all())

def create_vehicle(session: Session, vehicle_data: Vehicle) -> Vehicle:
    try:
        session.add(vehicle_data)
        session.commit()
        session.refresh(vehicle_data)
        return vehicle_data
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: Could not create vehicle")

def update_vehicle(session: Session, vehicle: Vehicle) -> Vehicle:
    existing_vehicle = get_vehicle_by_id(session, vehicle.vehicleId)
    
    if not existing_vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle with ID {vehicle.vehicleId} does not exist")
    
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle

def delete_vehicle(session: Session, vehicle_id: int) -> None:
    vehicle = get_vehicle_by_id(session, vehicle_id)
    
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"Vehicle with ID {vehicle_id} does not exist")
    
    session.delete(vehicle)
    session.commit()
