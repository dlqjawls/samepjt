from sqlmodel import Session, select
from sqlalchemy import func
from app.db.models.usage_history import UsageHistory
from app.db.models.vehicle import Vehicle
from app.db.models.module import Module
from app.db.models.option import Option
from app.db.crud.lut import usage_status
from app.utils.lut_constants import ItemType
from app.api.schemas.admin.usage_history_schema import (
    UsageHistoryGetResponse,
    UsageHistoryData,
    UsageHistoryItem,
    Pagination
)


class UsageHistoryService:
    @staticmethod
    def get_usage_history(session: Session, page: int, page_size: int, include_deleted: bool = False) -> UsageHistoryGetResponse:
        """
        사용 이력 데이터를 조회합니다.
        기본적으로는 soft delete 처리된(삭제된) 항목은 제외합니다.
        include_deleted를 True로 설정하면 삭제된 항목도 포함합니다.

        Args:
            session (Session): 데이터베이스 세션.
            page (int): 현재 페이지 번호 (1 이상의 값).
            page_size (int): 한 페이지당 항목 수.
            include_deleted (bool, optional): 삭제된 항목 포함 여부. 기본값은 False.

        Returns:
            UsageHistoryResponse: 사용 이력 조회 결과를 담은 응답 객체.
        """

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
                usage_status_name=usage_status.get_by_id(session, record.usage_status_id).usage_status_name,
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