from sqlmodel import Session, select
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from app.models.vehicle import Vehicle
from app.crud.base import CRUDBase
from app.utils.exceptions import DatabaseError, NotFoundError

class VehicleCRUD(CRUDBase[Vehicle]):
    def __init__(self):
        super().__init__(Vehicle, "vehicle_id")
        
        
    def get_first_available_vehicle(
            self,
            session: Session,
            status_id: int = 2  # INACTIVE
        ) -> Vehicle:
            """첫 번째 사용 가능한 차량 조회"""
            try:
                vehicle = session.exec(
                    select(self.model)
                    .where(
                        self.model.status_id == status_id,
                        self.model.deleted_at == None
                    )
                    .limit(1)
                ).first()

                if not vehicle:
                    raise NotFoundError(
                        message="No available vehicle found",
                        detail={
                            "status_id": status_id,
                            "error": "모든 차량이 사용 중입니다."
                        }
                    )

                return vehicle

            except SQLAlchemyError as e:
                raise DatabaseError(
                    message="Failed to fetch available vehicle",
                    detail={"error": str(e)}
                )

    
vehicle_crud = VehicleCRUD()