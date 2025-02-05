from typing import List
from sqlmodel import Session, select
from app.api.schemas.admin.vehicle_shema import VehicleItem, VehiclesData, VehiclesResponse, VehicleCreate
from app.crud.vehicle import vehicle_crud
from app.api.schemas.common import Coordinate
from app.models.vehicle import Vehicle
from app.utils.exceptions import DatabaseError, ConflictError
from app.utils.lut_constants import ITEM_STATUS, ITEM_STATUS_MAPPING
from app.utils.handle_transaction import handle_transaction
from datetime import datetime

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

    @staticmethod
    @handle_transaction
    def create_vehicle(session: Session, vehicle_data: VehicleCreate, user_pk: int) -> VehiclesResponse:
        """차량 등록 서비스"""
        # 1. VIN 중복 검사
        if vehicle_crud.get_by_vin(session, vehicle_data.vin):
            raise ConflictError(
                message="Vehicle already exists",
                detail={
                    "vin": vehicle_data.vin,
                    "error": "VIN already exists"
                }
            )

        # 2. 차량 번호 중복 검사
        if vehicle_crud.get_by_vehicle_number(session, vehicle_data.vehicle_number):
            raise ConflictError(
                message="Vehicle already exists",
                detail={
                    "vehicle_number": vehicle_data.vehicle_number,
                    "error": "Vehicle number already exists"
                }
            )

        # 3. 새 차량 생성
        new_vehicle = Vehicle(
            vin=vehicle_data.vin,
            vehicle_number=vehicle_data.vehicle_number,
            current_location=str(Coordinate(x=0.0, y=0.0)),  # 초기 위치는 (0,0)
            mileage=0.0,  # 초기 주행거리는 0
            status_id=ITEM_STATUS.INACTIVE,  # 초기 상태는 INACTIVE
            created_by=user_pk,
            updated_by=user_pk,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        vehicle_crud.create(session, new_vehicle)
        return VehiclesResponse.success(
            message="Vehicle registered successfully"
        )