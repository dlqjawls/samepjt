from typing import List
from sqlmodel import Session
from app.api.schemas.admin.vehicle_shema import VehicleItem, VehiclesData, VehiclesResponse
from app.crud.vehicle import vehicle_crud
from app.api.schemas.common import Coordinate
from app.models.vehicle import Vehicle
from app.utils.exceptions import DatabaseError
from app.utils.lut_constants import ITEM_STATUS, ITEM_STATUS_MAPPING

class VehicleService:
    @staticmethod
    def _convert_vehicle_data(vehicle: Vehicle) -> VehicleItem:
        """차량 데이터 변환"""
        if vehicle.vehicle_id is None:
            raise DatabaseError(
                message="Vehicle ID is required",
                detail={"vehicle": vehicle.dict()}
            )
            
        return VehicleItem(
            vehicle_id=vehicle.vehicle_id,
            vin=vehicle.vin,
            vehicle_number=vehicle.vehicle_number,
            current_location=Coordinate.from_str(vehicle.current_location),
            mileage=vehicle.mileage,
            last_maintenance_at=vehicle.last_maintenance_at,
            next_maintenance_at=vehicle.next_maintenance_at, 
            status=ITEM_STATUS_MAPPING.get(ITEM_STATUS(vehicle.status_id), "Unknown"),
            created_at=vehicle.created_at,
            created_by=vehicle.created_by,
            updated_at=vehicle.updated_at,
            updated_by=vehicle.updated_by
        )

    @staticmethod
    def get_vehicle_list(session: Session, page: int, page_size: int) -> VehiclesResponse:
        "관리자 차량 목록 조회 서비스"
        paginated_result = vehicle_crud.get_all(session, page, page_size)
        vehicles: List[Vehicle] = paginated_result["items"]
        
        # 차량 데이터 변환
        vehicle_items = [
            VehicleItem.parse_obj(
                VehicleService._convert_vehicle_data(vehicle)
            )
            for vehicle in vehicles
        ]

        vehicles_data = VehiclesData(
            vehicles=vehicle_items,
            pagination=paginated_result["pagination"]
        )

        return VehiclesResponse.success(
            data=vehicles_data,
            message="Vehicle data retrieved successfully"
        )