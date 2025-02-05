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

    
    def get_vehicle_type_name(self, type_id: int) -> str:
        """
        주어진 차량 유형 ID에 해당하는 이름을 반환합니다.
        (ITEM_TYPE_MAPPING을 활용)
        """
        from app.crud.lut import get_item_type_mapping
        mapping = get_item_type_mapping()
        return mapping.get(type_id, "Unknown")

vehicle_crud = VehicleCRUD()