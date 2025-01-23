from sqlmodel import select, Session
from app.models.vehicle import Vehicle
from typing import Union, List

def get_vehicle_by_id(session: Session, vehicle_id: int) -> Union[Vehicle, None]:
    statement = select(Vehicle).where(Vehicle.vehicleId == vehicle_id)
    return session.exec(statement).first()

def get_all_vehicles(session: Session) -> List[Vehicle]:
    statement = select(Vehicle)
    return list(session.exec(statement).all())

def create_vehicle(session: Session, vehicle_data: Vehicle) -> Vehicle:
    session.add(vehicle_data)
    session.commit()
    session.refresh(vehicle_data)
    return vehicle_data

def update_vehicle(session: Session, vehicle: Vehicle) -> Vehicle:
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle

def delete_vehicle(session: Session, vehicle: Vehicle) -> None:
    session.delete(vehicle)
    session.commit()