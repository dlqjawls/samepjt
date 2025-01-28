from sqlmodel import Session, select
from typing import List, Optional
from app.models.vehicle import Vehicle
from app.crud.base import CRUDBase
from app.utils.exceptions import DatabaseError

class VehicleCRUD(CRUDBase[Vehicle]):
    def __init__(self):
        super().__init__(Vehicle, "vehicle_id")
        
    def get_vehicles_by_status(
        self, 
        session: Session, 
        status_id: int
    ) -> List[Vehicle]:
        """
        특정 상태의 차량 목록 조회

        Args:
            session: DB 세션
            status_id: 차량 상태 ID

        Returns:
            List[Vehicle]: 조회된 차량 목록

        Raises:
            DatabaseError: 데이터베이스 조회 실패 시
        """
        try:
            query = (
                select(self.model)
                .where(self.model.status_id == status_id)
            )

            return list(session.exec(query).all())

        except Exception as e:
            raise DatabaseError(
                message="Failed to get vehicles by status",
                detail={
                    "status_id": status_id,
                    "error": str(e)
                }
            )

    def get_first_vehicle_by_status_id(
        self, 
        session: Session,
        status_id: int,
    ) -> Vehicle:
        """
        특정 상태에 해당하는 첫 번째 차량 조회

        Args:
            session: DB 세션
            status_id: 차량 상태 ID

        Returns:
            Optional[Vehicle]: 조회된 차량 또는 None

        Raises:
            DatabaseError: 데이터베이스 조회 실패 시
        """
        query = (
            select(self.model)
            .where(self.model.status_id == status_id)
        )

        vehicle = session.exec(query).first()
        if vehicle is None:
            raise DatabaseError(
                message="No available vehicle found",
                detail={
                    "status_id": status_id
                }
            )
            
        return vehicle
        
    
vehicle_crud = VehicleCRUD()