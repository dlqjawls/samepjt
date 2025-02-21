from datetime import datetime
from sqlmodel import Session, select
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from app.db.models.vehicle import Vehicle
from app.db.crud.base import CRUDBase
from app.utils.exceptions import DatabaseError, NotFoundError
from app.utils.lut_constants import ItemStatus

class VehicleCRUD(CRUDBase[Vehicle]):
    def __init__(self):
        super().__init__(Vehicle)

    def get_first_available_vehicle(self, session: Session, item_status_id: int = ItemStatus.INACTIVE.ID) -> Vehicle:
        """
        첫 번째 사용 가능한 차량을 조회합니다.

        Args:
            session (Session): 데이터베이스 세션.
            item_status_id (int): 차량 상태 ID (기본값: 2, INACTIVE).


        Returns:
            Vehicle: 사용 가능한 차량 객체.

        Raises:
            NotFoundError: 사용 가능한 차량이 없는 경우.
        """
        try:
            vehicle = session.exec(
                select(self.model)
                .where(
                    self.model.item_status_id == item_status_id,
                    self.model.deleted_at == None
                )
                .limit(1)

            ).first()

            if not vehicle:
                raise NotFoundError(
                    message="No available vehicle found",
                    detail={"item_status_id": item_status_id, "error": "모든 차량이 사용 중입니다."}
                )

            return vehicle

        except SQLAlchemyError as e:
            raise DatabaseError(
                message="Failed to fetch available vehicle",
                detail={"error": str(e)}
            )

    def get_by_id(self, session: Session, id: int) -> Optional[Vehicle]:
        """
        주어진 ID에 해당하는 차량을 조회합니다.

        Args:
            session (Session): 데이터베이스 세션.
            id (int): 차량 ID.

        Returns:
            Optional[Vehicle]: 차량 객체.
        """
        return self.get_by_field(session, id, "vehicle_id")
      
    def get_by_vin(self, session: Session, vin: str) -> Optional[Vehicle]:
        """
        주어진 VIN에 해당하는 차량을 조회합니다.

        Args:
            session (Session): 데이터베이스 세션.
            vin (str): VIN.

        Returns:
            Optional[Vehicle]: 차량 객체.
        """
        return self.get_by_field(session, vin, "vin")
      
    def get_by_vehicle_number(self, session: Session, vehicle_number: str) -> Optional[Vehicle]:
        """
        주어진 차량 번호에 해당하는 차량을 조회합니다.

        Args:
            session (Session): 데이터베이스 세션.
            vehicle_number (str): 차량 번호.

        Returns:
            Optional[Vehicle]: 차량 객체.
        """
        return self.get_by_field(session, vehicle_number, "vehicle_number")
      
      
vehicle_crud = VehicleCRUD()