from typing import List
from sqlmodel import Session
from app.api.schemas.admin.vehicle_schema import VehicleItem, VehiclesData, VehiclesResponse, VehicleCreate, VehicleUpdateRequest, VehicleUpdateResponse, VehicleDeleteResponse
from app.db.crud.vehicle import vehicle_crud
from app.db.crud.usage_history import usage_history_crud
from app.db.crud.maintenance_history import maintenance_history_crud
from app.api.schemas.common import Coordinate
from app.db.models.vehicle import Vehicle
from app.utils.exceptions import DatabaseError, ConflictError, NotFoundError
from app.utils.handle_transaction import handle_transaction
from datetime import datetime
from sqlalchemy import select
from app.utils.lut_constants import ItemStatus, ItemType, UsageStatus
from app.db.models.usage_history import UsageHistory

class VehicleService:
  
    @staticmethod
    def _check_vin_exists(session: Session, vin: str) -> None:
        """VIN 중복 검사"""
        if vehicle_crud.get_by_vin(session, vin):
            raise ConflictError(
                message="Vehicle already exists",
                detail={"vin": vin, "error": "VIN already exists"}
            )
            
    @staticmethod
    def _check_vehicle_number_exists(session: Session, vehicle_number: str) -> None:
        """차량 번호 중복 검사"""
        if vehicle_crud.get_by_vehicle_number(session, vehicle_number):
            raise ConflictError(
                message="Vehicle number already exists",
                detail={
                    "vehicle_number": vehicle_number,
                    "error": "Vehicle number already exists"
                }
            )

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
            item_status_name= ItemStatus.get_name(vehicle.item_status_id),
            created_at=vehicle.created_at,
            created_by=vehicle.created_by,
            updated_at=vehicle.updated_at,
            updated_by=vehicle.updated_by
        )

    @staticmethod
    def get_vehicle_list(session: Session, page: int, page_size: int) -> VehiclesResponse:
        "관리자 차량 목록 조회 서비스"
        
        # 차량 목록 조회
        paginated_result = vehicle_crud.paginate(session, page, page_size)
        vehicles: List[Vehicle] = paginated_result["items"]
        
        # 차량 데이터 변환
        vehicle_items = [
            VehicleItem.parse_obj(
                VehicleService._convert_vehicle_data(vehicle)
            )
            for vehicle in vehicles
        ]

        # 차량 목록 데이터 생성
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
        # VIN 중복 검사
        VehicleService._check_vin_exists(session, vehicle_data.vin)

        # 차량 번호 중복 검사
        VehicleService._check_vehicle_number_exists(session, vehicle_data.vehicle_number)

        # 새 차량 생성
        new_vehicle = Vehicle(
            vin=vehicle_data.vin,
            vehicle_number=vehicle_data.vehicle_number,
            current_location=str(Coordinate(x=0.0, y=0.0)),  # 초기 위치는 (0,0)
            mileage=0.0,  # 초기 주행거리는 0
            item_status_id=ItemStatus.INACTIVE,  # 초기 상태는 INACTIVE
            created_by=user_pk,
            updated_by=user_pk,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        vehicle_crud.create(session, new_vehicle)
        return VehiclesResponse.success(
            message="Vehicle registered successfully"
        )

    @staticmethod
    @handle_transaction
    def update_vehicle(session: Session, vehicle_data: VehicleUpdateRequest, vehicle_id: int, user_pk: int) -> VehicleUpdateResponse:
        """차량 정보 수정 서비스"""
        # 차량 존재 여부 확인
        vehicle = vehicle_crud.get_by_id(session, vehicle_id)
        if not vehicle:
            raise NotFoundError(
                message="Vehicle not found",
                detail={"vehicle_id": vehicle_id}
            )

        # 차량 번호 중복 검사 (차량 번호가 변경되는 경우에만)
        if vehicle_data.vehicle_number and vehicle_data.vehicle_number != vehicle.vehicle_number:
            VehicleService._check_vehicle_number_exists(session, vehicle_data.vehicle_number)

        # 업데이트 데이터 준비
        update_data = vehicle_data.dict(exclude_unset=True)
        update_data["updated_by"] = user_pk
        update_data["updated_at"] = datetime.now()
        
        # 차량 업데이트
        vehicle_crud.update(session, vehicle_id, update_data, "vehicle_id")
        
        return VehicleUpdateResponse.success(
            message="Vehicle updated successfully"
        )

    @staticmethod
    @handle_transaction
    def delete_vehicle(session: Session, vehicle_id: int, user_pk: int) -> VehicleDeleteResponse:
        """차량 삭제 서비스"""
        
        # 차량 존재 여부 확인
        vehicle = vehicle_crud.get_by_id(session, vehicle_id)
        if not vehicle:
            raise NotFoundError(
                message="Vehicle not found",
                detail={"vehicle_id": vehicle_id}
            )
        
        # 차량이 현재 사용 중인지 UsageHistory 테이블에서 확인
        usage_history_data = usage_history_crud.get_item_usage_history(session, vehicle_id, ItemType.VEHICLE.ID)
        usage_history_items = usage_history_data.get("items", [])
        if any(history.usage_status_id == UsageStatus.IN_USE.ID for history in usage_history_items):
            raise ConflictError(
                message="Vehicle is currently in use and cannot be deleted",
                detail={"vehicle_id": vehicle_id}
            )
            
        # 차량이 현재 정비 중인지 maintenance_history 테이블에서 확인
        maintenance_history = maintenance_history_crud.get_by_field(session, vehicle_id, "vehicle_id")
        if maintenance_history:
            raise ConflictError(
                message="Vehicle is currently under maintenance and cannot be deleted",
                detail={"vehicle_id": vehicle_id}
            )

        # 차량 삭제
        vehicle_crud.soft_delete(session, vehicle_id, "vehicle_id")

        return VehicleDeleteResponse(
            resultCode="SUCCESS",
            message="Vehicle deleted successfully"
        )   
        