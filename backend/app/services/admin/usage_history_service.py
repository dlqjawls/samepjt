from sqlmodel import Session, select
from sqlalchemy import func
from app.db.models.usage_history import UsageHistory
from app.db.models.vehicle import Vehicle
from app.db.models.module import Module
from app.db.models.option import Option
from app.utils.lut_constants import ItemType, UsageStatus
from app.api.schemas.admin.usage_history_schema import (
    UsageHistoryGetResponse,
    UsageHistoryData,
    UsageHistoryItem,
    Pagination
)


class UsageHistoryService:
    @staticmethod
    def get_usage_history(session: Session, page: int, page_size: int, include_deleted: bool = False) -> UsageHistoryGetResponse:
        """사용 이력 데이터를 조회합니다."""

        offset = (page - 1) * page_size  # 항상 정의되도록 위로 이동

        if not include_deleted:
            filter_condition = (
                ((UsageHistory.item_type_id == ItemType.VEHICLE.ID) &
                 (UsageHistory.item_id==(select(Vehicle.vehicle_id)
                                               .where(Vehicle.deleted_at == None)))) |
                ((UsageHistory.item_type_id == ItemType.MODULE.ID) &
                 (UsageHistory.item_id==(select(Module.module_id)
                                               .where(Module.deleted_at == None)))) |
                ((UsageHistory.item_type_id == ItemType.OPTION.ID) &
                 (UsageHistory.item_id==(select(Option.option_id)
                                               .where(Option.deleted_at == None))))
            )
            count_stmt = select(func.count()).select_from(UsageHistory).where(filter_condition)
            records_stmt = select(UsageHistory).where(filter_condition)
        else:
            count_stmt = select(func.count()).select_from(UsageHistory)
            records_stmt = select(UsageHistory)

        total_items = session.exec(count_stmt).one()
        records = session.exec(records_stmt.offset(offset).limit(page_size)).all()
        

        # DB 레코드를 스키마 항목으로 매핑
        usage_history_items = [
            UsageHistoryItem(
                usage_id=record.usage_id,
                rent_id=record.rent_id,
                item_id=record.item_id,
                item_type_name=ItemType.get_name(record.item_type_id),
                usage_status_name=UsageStatus.get_name(record.usage_status_id),
                created_at=record.created_at,
                updated_at=record.updated_at
            )
            for record in records
        ]

        total_pages = (total_items + page_size - 1) // page_size if total_items else 0
        pagination = Pagination(
            currentPage=page,
            totalPages=total_pages,
            totalItems=total_items,
            pageSize=page_size
        )
        data = UsageHistoryData(
            usage_history=usage_history_items,
            pagination=pagination
        )
        return UsageHistoryGetResponse(
            resultCode="SUCCESS",
            message="Usage history retrieved successfully",
            data=data
        ) 