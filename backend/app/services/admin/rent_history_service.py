from sqlmodel import Session
from app.api.schemas.common import Coordinate
from app.db.models.rent_history import RentHistory
from app.utils.exceptions import NotFoundError, DatabaseError
from app.db.crud.usage_history import usage_history_crud
from app.db.crud.vehicle import vehicle_crud
from app.db.crud.option import option_crud
from app.db.crud.rent_history import rent_history_crud
from app.api.schemas.admin.rent_history_schema import RentHistoryResponse, RentHistoryData, RentHistoryItem
from app.utils.lut_constants import ItemType, RentStatus, LUTConstants 


class RentHistoryService:
    @staticmethod
    def _validate_vehicle(vehicle_id: int, session: Session) -> str:
        """차량 정보 검증 및 조회"""
        vehicle = vehicle_crud.get_by_id(session, vehicle_id)
        if not vehicle:
            raise DatabaseError(
                message="Vehicle not found",
                detail={"vehicle_id": vehicle_id}
            )
        if not vehicle.vehicle_number:
            raise DatabaseError(
                message="Vehicle number is required",
                detail={"vehicle_id": vehicle_id}
            )
        return vehicle.vehicle_number

    @staticmethod
    def _validate_option(option_id: int, session: Session) -> str:
        """옵션 정보 검증 및 조회"""
        option = option_crud.get_by_id(session, option_id)
        if not option:
            raise DatabaseError(
                message="Option not found",
                detail={"option_id": option_id}
            )
        if not option.option_type_id:
            raise DatabaseError(
                message="Option type ID is required",
                detail={"option_id": option_id}
            )
        return str(option.option_type_id)

    @staticmethod
    def _process_usage_entries(session: Session, rent_id: int) -> tuple[str, list[str]]:
        """사용 기록 처리"""
        usage_entries = usage_history_crud.get_usage_entries(session, rent_id)
        if not usage_entries:
            raise DatabaseError(
                message="No usage entries found",
                detail={"rent_id": rent_id}
            )

        vehicle_number = ""
        option_type_ids: list[str] = []
        
        for entry in usage_entries:
            if entry.item_type_id == ItemType.VEHICLE:
                vehicle_number = RentHistoryService._validate_vehicle(entry.item_id, session)
            elif entry.item_type_id == ItemType.OPTION:
                option_type_id = RentHistoryService._validate_option(entry.item_id, session)
                option_type_ids.append(option_type_id)

        if not vehicle_number:
            raise DatabaseError(
                message="Vehicle information is required",
                detail={"rent_id": rent_id}
            )
                    
        return vehicle_number, option_type_ids

    @staticmethod
    def _create_rent_history_item(rent: RentHistory, vehicle_number: str, option_type_ids: list[str]) -> RentHistoryItem:
        """RentHistoryItem 생성"""
        if not isinstance(rent.rent_id, int):
            raise NotFoundError(message="Invalid rent_id", detail={"rent_id": str(rent.rent_id)})
            
        return RentHistoryItem(
            rent_id=rent.rent_id,
            user_pk=rent.user_pk,
            vehicle_number=vehicle_number,
            option_types=",".join(option_type_ids),
            departure_location=Coordinate.from_str(rent.departure_location),
            arrival_location=Coordinate.from_str(rent.arrival_location),
            cost=float(rent.cost) if rent.cost else 0.0,
            mileage=float(rent.mileage) if rent.mileage else 0.0,
            status=LUTConstants.RENT_STATUS_NAMES.get(RentStatus(rent.status_id), "unknown"),
            created_at=rent.created_at,
            updated_at=rent.updated_at
        )

    @staticmethod
    def get_rent_history(session: Session, page: int = 1, page_size: int = 10) -> RentHistoryResponse:
        """렌트 히스토리 조회"""
        paginated_result = rent_history_crud.paginate(session, page, page_size)
        
        rent_history_items: list[RentHistoryItem] = []
        for rent in paginated_result["items"]:
            if not isinstance(rent.rent_id, int):
                continue

            vehicle_number, option_type_ids = RentHistoryService._process_usage_entries(session, rent.rent_id)
            rent_history_items.append(
                RentHistoryService._create_rent_history_item(rent, vehicle_number, option_type_ids)
            )

        return RentHistoryResponse.success(
            data=RentHistoryData(
                rent_history=rent_history_items,
                pagination=paginated_result["pagination"]
            ),
            message="Rent logs retrieved successfully"
        )