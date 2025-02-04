from sqlmodel import Session
from typing import List, Dict
from app.models.rent_history import RentHistory
from app.utils.exceptions import NotFoundError
from app.crud.usage_history import usage_history_crud
from app.crud.vehicle import vehicle_crud
from app.crud.option import option_crud
from app.crud.rent_history import rent_history_crud
from app.api.schemas.admin.rent_history_schema import RentHistoryResponse, RentHistoryData, RentHistoryItem
from app.api.schemas.common import Coordinate, Pagination

# TODO: 렌트 상태 매핑 추가
rent_status_mapping = {
    1: "in_progress",
    2: "completed",
    3: "cancelled"
}

class RentHistoryService:
    VEHICLE_TYPE_ID = 1
    OPTION_TYPE_ID = 3

    @staticmethod
    def parse_location(loc_str: str) -> Coordinate:
        try:
            parts = loc_str.split(',')
            if len(parts) == 2:
                return Coordinate(x=float(parts[0]), y=float(parts[1]))
            return Coordinate(x=0.0, y=0.0)
        except Exception:
            return Coordinate(x=0.0, y=0.0)

    @staticmethod
    def get_vehicle_number(session: Session, item_id: int) -> str:
        vehicle_obj = vehicle_crud.get_by_id(session, item_id)
        if not vehicle_obj or not vehicle_obj.vehicle_number:
            raise NotFoundError(message="Vehicle not found", detail={"item_id": item_id})
        return vehicle_obj.vehicle_number

    @staticmethod
    def get_option_type_ids(session: Session, item_id: int) -> str:
        option_obj = option_crud.get_by_id(session, item_id)
        if not option_obj:
            raise NotFoundError(message="Option type not found", detail={"item_id": item_id})
        return str(option_obj.option_type_id)

    @staticmethod
    def get_rent_history_items(session: Session, results: List[RentHistory]) -> List[RentHistoryItem]:
        rent_history_items = []
        for rent in results:
            if not rent.rent_id:
                raise NotFoundError(
                    message="Rent ID is missing",
                    detail={"rent": rent}
                )
            usage_entries = usage_history_crud.get_usage_entries(session, rent.rent_id)
            vehicle_number = ""
            option_type_ids = []
            for ue in usage_entries:
                if ue.item_type_id == RentHistoryService.VEHICLE_TYPE_ID:
                    vehicle_number = RentHistoryService.get_vehicle_number(session, ue.item_id)
                elif ue.item_type_id == RentHistoryService.OPTION_TYPE_ID:
                    option_type_ids.append(RentHistoryService.get_option_type_ids(session, ue.item_id))
            rent_history_items.append(RentHistoryItem(
                rent_id=rent.rent_id,
                user_pk=rent.user_pk,
                vehicle_number=vehicle_number,
                option_types=",".join(option_type_ids),
                departure_location=RentHistoryService.parse_location(rent.departure_location),
                arrival_location=RentHistoryService.parse_location(rent.arrival_location),
                cost=float(rent.cost) if rent.cost else 0.0,
                mileage=float(rent.mileage) if rent.mileage else 0.0,
                status=rent_status_mapping.get(rent.status_id, "unknown"),
                created_at=rent.created_at,
                updated_at=rent.updated_at
            ))
        return rent_history_items

    @staticmethod
    def get_rent_history(session: Session, page: int = 1, page_size: int = 10) -> RentHistoryResponse:
        # CRUD 계층에서 페이징 처리된 데이터를 조회
        paginated_result = rent_history_crud.get_all(session, page, page_size)
        results = paginated_result["items"]
        pagination = paginated_result["pagination"]

        rent_history_items = RentHistoryService.get_rent_history_items(session, list(results))

        return RentHistoryResponse.success(
            data=RentHistoryData(
                rent_history=rent_history_items,
                pagination=Pagination(
                    currentPage=pagination["currentPage"],
                    totalPages=pagination["totalPages"],
                    totalItems=pagination["totalItems"],
                    pageSize=pagination["pageSize"],
                )
            ),
            message="Rent logs retrieved successfully"
        )